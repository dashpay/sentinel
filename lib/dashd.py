import pdb
from pprint import pprint
"""
Dashd interface
"""

import sys, os
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
import config
import base58
import subprocess
import json
import io
import re
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from masternode import Masternode

class DashDaemon():
    def __init__(self, **kwargs):
        host = kwargs.get('host', '127.0.0.1')
        user = kwargs.get('user')
        password = kwargs.get('password')
        port = kwargs.get('port')

        creds = (user, password, host, port)
        self.rpc_connection = AuthServiceProxy("http://{0}:{1}@{2}:{3}".format(*creds))

        # memoize calls to some dashd methods
        self.governance_info = None

    @classmethod
    def from_dash_conf(self, dash_dot_conf):
        config_text = DashConfig.slurp_config_file(dash_dot_conf)
        creds = DashConfig.get_rpc_creds(config_text)

        return self(
            user     = creds.get('user'),
            password = creds.get('password'),
            port     = creds.get('port')
        )

    def rpc_command(self, *params):
        return self.rpc_connection.__getattr__(params[0])(*params[1:])

    # common RPC convenience methods
    def is_testnet(self):
        return self.rpc_command('getinfo')['testnet']

    def get_masternodes(self):
        mnlist = self.rpc_command('masternodelist', 'full')
        return [ Masternode(k, v) for (k, v) in mnlist.items()]

    def get_current_masternode_vin(self):
        from dashlib import parse_masternode_status_vin

        my_vin = None

        try:
            status = self.rpc_command('masternode', 'status')
            my_vin = parse_masternode_status_vin(status['vin'])
        except JSONRPCException as e:
            pass

        return my_vin

    def governance_quorum(self):
        total_masternodes = self.rpc_command('masternode', 'count')
        govinfo = self.rpc_command('getgovernanceinfo')
        min_quorum = govinfo['governanceminquorum']

        # the minimum quorum is calculated based on the number of masternodes
        quorum = max( min_quorum, total_masternodes / min_quorum )
        return quorum

    @property
    def govinfo(self):
        if ( not self.governance_info ):
            self.governance_info = self.rpc_command('getgovernanceinfo')
        return self.governance_info

    # governance info convenience methods
    def superblockcycle(self):
        return self.govinfo['superblockcycle']

    def governanceminquorum(self):
        return self.govinfo['governanceminquorum']

    def proposalfee(self):
        return self.govinfo['proposalfee']

    def last_superblock_height(self):
        height = self.rpc_command('getblockcount')
        cycle  = self.superblockcycle()
        return cycle * (height / cycle)

    def next_superblock_height(self):
        return self.last_superblock_height() + self.superblockcycle()

    def is_masternode(self):
        return not (self.get_current_masternode_vin() == None)

class DashConfig():

    @classmethod
    def slurp_config_file(self, filename):
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

    @classmethod
    def get_rpc_creds(self, data):
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
