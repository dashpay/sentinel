import pdb
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from pprint import pprint
import socket
import sys
import config
sys.path.append("lib")

from dashd import DashDaemon
from dashd import DashConfig


# get JSONRPC credentials from dash.conf
data = DashConfig.slurp_config_file(config.dash_conf)
creds = DashConfig.get_rpc_creds(data)

try:
    dashd = DashDaemon(
        user     = creds.get('user'),
        password = creds.get('password'),
        port     = creds.get('port')
    )
    print dashd.rpc_command('getbestblockhash')
    print dashd.rpc_command('getblock', '000000167d8064d2b6cdc62c46c989df7b5c623df6796b7bcb545a29f0a550b7')
except JSONRPCException as e:
    print "JSONRPC Exception: %s" % e.message
except socket.error as e:
    print "Socket Error: %s" % e.strerror

# batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
#commands = [ [ "getblockhash", height] for height in range(100) ]
#block_hashes = rpc_connection.batch_(commands)
#blocks = rpc_connection.batch_([ [ "getblock", h ] for h in block_hashes ])
#block_times = [ block["time"] for block in blocks ]
#print(block_times)
