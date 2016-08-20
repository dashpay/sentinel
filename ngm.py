from pprint import pprint
import config
import re
import sys
import io

print config.db_config['hostname']
print config.dash_conf
print config.network

port = 9998 if ( config.network == 'mainnet' ) else 19998

def get_rpc_creds_from_dashconf(filename):
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

    # get rpc info from dash.conf
    match = re.findall('rpc(user|password|port)=(\w+)', data)
    dikt = {}
    for tupl in match:
        dikt[ tupl[0] ] = tupl[1]

    return dikt

rpc_creds = get_rpc_creds_from_dashconf( config.dash_conf )
pprint(rpc_creds)

try:
  port = config.rpcport
except AttributeError:
  port = rpc_creds['port'] if ( 'port' in rpc_creds ) else port 

print "port = %s" % port


