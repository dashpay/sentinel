import pdb
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from pprint import pprint
import socket
import io
import sys
import re
import config
sys.path.append("lib")

from dashd import DashDaemon


def slurp_config_file(filename):
    # read dash.conf config but skip commented lines
    f = io.open(filename)
    lines = []
    for line in f:
        if re.match('^\s*#', line):
            continue
        lines.append(line)
    f.close()

    # data is dash.conf without commented lines
    data = ''.join(lines)

    return data


def get_rpc_creds(data):
    # get rpc info from dash.conf
    match = re.findall('rpc(user|password|port)=(\w+)', data)

    # python <= 2.6
    #d = dict((key, value) for (key, value) in match)

    # python >= 2.7
    creds = { key: value for (key, value) in match }

    # standard Dash defaults...
    default_port = 9998 if ( config.network == 'mainnet' ) else 19998

    # use default port for network if not specified in dash.conf
    if not ( 'port' in creds ):
        creds[u'port'] = default_port

    # convert to an int if taken from dash.conf
    creds[u'port'] = int(creds[u'port'])

    # return a dictionary with RPC credential key, value pairs
    return creds

# get JSONRPC credentials from dash.conf
data = slurp_config_file(config.dash_conf)
creds = get_rpc_creds(data)

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
