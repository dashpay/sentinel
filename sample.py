from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from pprint import pprint
import socket

rpc_user = 'dashrpc'
rpc_password = 'ZZZZZZsdrtyujk3498y7dcpoi3ue49orfjfpQKmXjzto'
rpc_port = 19998

rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:%s"%(rpc_user, rpc_password, rpc_port))

try:
    best_block_hash = rpc_connection.getbestblockhash()
    print(rpc_connection.getblockz(best_block_hash))
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

