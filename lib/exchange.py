#! /usr/bin/python3

import struct
import decimal
D = decimal.Decimal
import logging

from . import (util, config, exceptions, bitcoin, util)

FORMAT = '>QQQQ'
LENGTH = 8 + 8 + 8 + 8
ID = 90

def validate (db, source, give_asset, give_quantity, get_asset, get_quantity, destination, btc_amount, block_index):
    problems = []
    cursor = db.cursor()

    if not config.TESTNET:
        problems.append('exchanges disabled')

    if get_asset == config.BTC:
        if destination:
            if btc_amount < get_amount:
                problems.append('insufficient {}'.format(config.BTC))
        else:
            problems.append('no destination')
    elif destination:
        problems.append('unnecessary destination')

    if give_asset == config.BTC:
        problems.append('cannot give {}'.format(config.BTC))

    if not isinstance(give_quantity, int):
        problems.append('give_quantity must be in satoshis')
        return problems
    if not isinstance(get_quantity, int):
        problems.append('get_quantity must be in satoshis')
        return problems

    if give_quantity <= 0: problems.append('non‐positive give quantity')
    if get_quantity <= 0: problems.append('non‐positive get quantity')

    if not give_quantity or not get_quantity:
        problems.append('zero give or zero get')
    cursor.execute('select * from issuances where (status = ? and asset = ?)', ('valid', give_asset))
    if give_asset not in (config.BTC, config.XCP) and not cursor.fetchall():
        problems.append('no such asset to give ({})'.format(give_asset))
    cursor.execute('select * from issuances where (status = ? and asset = ?)', ('valid', get_asset))
    if get_asset not in (config.BTC, config.XCP) and not cursor.fetchall():
        problems.append('no such asset to get ({})'.format(get_asset))

    # For SQLite3
    if give_quantity > config.MAX_INT or get_quantity > config.MAX_INT:
        problems.append('integer overflow')

    cursor.close()
    return problems

def compose (db, source, give_asset, give_quantity, get_asset, get_quantity):
    cursor = db.cursor()
    balances = list(cursor.execute('''SELECT * FROM balances WHERE (address = ? AND asset = ?)''', (source, give_asset)))
    if give_asset != config.BTC and (not balances or balances[0]['quantity'] < give_quantity):
        raise exceptions.ExchangeError('insufficient funds')

    if get_asset == config.BTC:
        destination, btc_amount = source, get_quantity
    else:
        destination, btc_amount = None, None

    problems = validate(db, source, give_asset, give_quantity, get_asset, get_quantity, destination, btc_amount, util.last_block(db)['block_index'])
    if problems: raise exceptions.ExchangeError(problems)

    give_id = util.asset_id(give_asset)
    get_id = util.asset_id(get_asset)
    data = struct.pack(config.TXTYPE_FORMAT, ID)
    data += struct.pack(FORMAT, give_id, give_quantity, get_id, get_quantity)
    cursor.close()

    return (source, [], data)

# TODO
def parse (db, tx, message):
    cursor = db.cursor()

    # Unpack message.
    try:
        assert len(message) == LENGTH
        give_id, give_quantity, get_id, get_quantity, expiration, fee_required = struct.unpack(FORMAT, message)
        give_asset = util.asset_name(give_id)
        get_asset = util.asset_name(get_id)
        status = 'open'
    except (AssertionError, struct.error) as e:
        give_asset, give_quantity, get_asset, get_quantity, expiration, fee_required = 0, 0, 0, 0, 0, 0
        status = 'invalid: could not unpack'

    price = 0
    if status == 'open':
        try: price = util.price(get_quantity, give_quantity, tx['block_index'])
        except Exception as e: pass

        # Overorder
        cursor.execute('''SELECT * FROM balances \
                                      WHERE (address = ? AND asset = ?)''', (tx['source'], give_asset))
        balances = list(cursor)
        if give_asset != config.BTC:
            if not balances:
                give_quantity = 0
            else:
                balance = balances[0]['quantity']
                if balance < give_quantity:
                    give_quantity = balance
                    get_quantity = int(price * give_quantity)

        problems = validate(db, tx['source'], give_asset, give_quantity, get_asset, get_quantity, expiration, fee_required, tx['block_index'])
        if problems: status = 'invalid: ' + '; '.join(problems)

    # Debit give quantity. (Escrow.)
    if status == 'open':
        if give_asset != config.BTC:  # No need (or way) to debit BTC.
            util.debit(db, tx['block_index'], tx['source'], give_asset, give_quantity, action='open order', event=tx['tx_hash'])

    # Add parsed transaction to message-type–specific table.
    bindings = {
        'tx_index': tx['tx_index'],
        'tx_hash': tx['tx_hash'],
        'block_index': tx['block_index'],
        'source': tx['source'],
        'give_asset': give_asset,
        'give_quantity': give_quantity,
        'give_remaining': give_quantity,
        'get_asset': get_asset,
        'get_quantity': get_quantity,
        'get_remaining': get_quantity,
        'expiration': expiration,
        'expire_index': tx['block_index'] + expiration,
        'fee_required': fee_required,
        'fee_required_remaining': fee_required,
        'fee_provided': tx['fee'],
        'fee_provided_remaining': tx['fee'],
        'status': status,
    }
    sql='insert into orders values(:tx_index, :tx_hash, :block_index, :source, :give_asset, :give_quantity, :give_remaining, :get_asset, :get_quantity, :get_remaining, :expiration, :expire_index, :fee_required, :fee_required_remaining, :fee_provided, :fee_provided_remaining, :status)'
    cursor.execute(sql, bindings)

    # Match.
    if status == 'open' and tx['block_index'] != config.MEMPOOL_BLOCK_INDEX:
        match(db, tx)

    cursor.close()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
