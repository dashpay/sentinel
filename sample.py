from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from pprint import pprint
import socket
import io
import sys
import re
import config


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
rpc_config = get_rpc_creds(data)

# convenience list for format string
creds = [ rpc_config.get('user'), rpc_config.get('password'), rpc_config.get('port') ]
rpc_connection = AuthServiceProxy("http://{0}:{1}@127.0.0.1:{2}".format(*creds))

try:
    best_block_hash = rpc_connection.getbestblockhash()
    print(rpc_connection.getblock(best_block_hash))
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
