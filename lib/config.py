import sys
import os

"""Variables prefixed with `DEFAULT` should be able to be overridden by
configuration file and command‐line arguments."""

UNIT = 100000000        # The same across assets.


# Versions
VERSION_MAJOR = 9
VERSION_MINOR = 42
VERSION_REVISION = 0
VERSION_STRING = str(VERSION_MAJOR) + '.' + str(VERSION_MINOR) + '.' + str(VERSION_REVISION)


# Czarparty protocol
TXTYPE_FORMAT = '>I'

TWO_WEEKS = 2 * 7 * 24 * 3600
MAX_EXPIRATION = 4 * 2016   # Two months

MEMPOOL_BLOCK_HASH = 'mempool'
MEMPOOL_BLOCK_INDEX = 9999999


# SQLite3
MAX_INT = 2**63 - 1


# Czarcoin Core
OP_RETURN_MAX_SIZE = 40 # bytes


# Currency agnosticism
CZR = 'CZR'
XZR = 'XZR'

CZR_NAME = 'Czarcoin'
CZR_CLIENT = 'czarcoind'
XZR_NAME = 'Czarparty'
XZR_CLIENT = 'czarpartyd'

DEFAULT_RPC_PORT_TESTNET = 17700
DEFAULT_RPC_PORT = 7700

DEFAULT_BACKEND_RPC_PORT_TESTNET = 18816
DEFAULT_BACKEND_RPC_PORT = 8816

UNSPENDABLE_TESTNET =  'mvCzarpartyXXXXXXXXXXXXXXXXXW24Hef'
#UNSPENDABLE_MAINNET = '7CzarpartyXXXXXXXXXXXXXXXXXXUWLpVr'
UNSPENDABLE_MAINNET = '7CzarpartyXXXXXXXXXXXXXXXXXXTzqJss'

ADDRESSVERSION_TESTNET = b'\x6f'
# PRIVATEKEY_VERSION_TESTNET =
ADDRESSVERSION_MAINNET = b'\x0f'
# PRIVATEKEY_VERSION_MAINNET =
MAGIC_BYTES_TESTNET = b'\x63\x7a\x72\x74'   # For bip-0010
MAGIC_BYTES_MAINNET = b'\x63\x7a\x61\x72'   # For bip-0010

BLOCK_FIRST_TESTNET_TESTCOIN = 154908
BURN_START_TESTNET_TESTCOIN = 154908
BURN_END_TESTNET_TESTCOIN = 4017708     # Fifty years, at ten minutes per block.

BLOCK_FIRST_TESTNET = 154908
BURN_START_TESTNET = 154908
BURN_END_TESTNET = 4017708              # Fifty years, at ten minutes per block.

BLOCK_FIRST_MAINNET_TESTCOIN = 278270
BURN_START_MAINNET_TESTCOIN = 278310
BURN_END_MAINNET_TESTCOIN = 2500000     # A long time.

BLOCK_FIRST_MAINNET = 4911
BURN_START_MAINNET = 4912
# Setting Burn Period to about 100 Years
#BURN_END_MAINNET = 283810
BURN_END_MAINNET = 25000000

MAX_BURN_BY_ADDRESS = 1000000 * UNIT 	# 1M CZR.
BURN_MULTIPLIER = 100					# 100 XZR per 1 CZR


# Protocol defaults
# NOTE: If the DUST_SIZE constants are changed, they MUST also be changed in czarblockd/lib/config.py as well
    # TODO: This should be updated, given their new configurability.
# TODO: The dust values should be lowered by 90%, once transactions with smaller outputs start confirming faster: <https://github.com/mastercoin-MSC/spec/issues/192>
#DEFAULT_REGULAR_DUST_SIZE = 5430         # TODO: This is just a guess. I got it down to 5530 satoshis.
#DEFAULT_MULTISIG_DUST_SIZE = 7800        # <https://bitcointalk.org/index.php?topic=528023.msg7469941#msg7469941>
#DEFAULT_OP_RETURN_VALUE = 0
#DEFAULT_FEE_PER_KB = 10000                # Czarcoin Core default is 10000.  # TODO: Lower 10x later, too.
DEFAULT_REGULAR_DUST_SIZE = UNIT 	  # 1 CZR; there is not dust limit in Czarcoin, but every txout < 1 CZR, cost 1 CZR in fee
DEFAULT_MULTISIG_DUST_SIZE = UNIT * 2 # 2 CZR.
DEFAULT_OP_RETURN_VALUE = 0 		  # 0 CZR.
DEFAULT_FEE_PER_KB = UNIT             # 1 CZR.

# UI defaults
DEFAULT_FEE_FRACTION_REQUIRED = .009   # 0.90%
DEFAULT_FEE_FRACTION_PROVIDED = .01    # 1.00%
