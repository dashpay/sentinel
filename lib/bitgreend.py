"""
bitgreend JSONRPC interface
"""
import time
from decimal import Decimal
from masternode import Masternode
from bitcoinrpc.authproxy import JSONRPCException
import requests
import json
import base58
import config
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))


class BitgreenDaemon():
    def __init__(self, **kwargs):
        host = kwargs.get('host', '127.0.0.1')
        user = kwargs.get('user')
        password = kwargs.get('password')
        port = kwargs.get('port')

        self.creds = (user, password, host, port)

        # memoize calls to some bitgreend methods
        self.governance_info = None
        self.gobject_votes = {}

        self.connection = None

    def rpc_command(self, *params):
        payload = {'id': 1, 'method': params[0], 'rpc': '1.0'}
        if len(params) > 1:
            payload['params'] = params[1:]

        try:
            r = requests.post(
                "http://{0}:{1}@{2}:{3}".format(*self.creds), data=json.dumps(payload))
            response = json.loads(r.text)
            if response['error'] is not None:
                raise JSONRPCException(response['error'])
            elif 'result' not in response:
                raise JSONRPCException({
                    'code': -343, 'message': 'missing JSON-RPC result'})
            return response['result']
        except:
            raise Exception

    @classmethod
    def from_bitgreen_conf(self, bitgreen_dot_conf):
        from bitgreen_config import BitgreenConfig
        config_text = BitgreenConfig.slurp_config_file(bitgreen_dot_conf)
        creds = BitgreenConfig.get_rpc_creds(config_text, config.network)

        creds[u'host'] = config.rpc_host

        return self(**creds)

    # common RPC convenience methods

    def get_masternodes(self):
        mnlist = self.rpc_command('masternodelist', 'full')
        return [Masternode(k, v) for (k, v) in mnlist.items()]

    def get_current_masternode_vin(self):
        from bitgreenlib import parse_masternode_status_vin

        my_vin = None

        try:
            status = self.rpc_command('masternode', 'status')
            mn_outpoint = status.get('outpoint') or status.get('vin')
            my_vin = parse_masternode_status_vin(mn_outpoint)
        except JSONRPCException as e:
            pass

        return my_vin

    def governance_quorum(self):
        # TODO: expensive call, so memoize this
        total_masternodes = self.rpc_command('masternode', 'count', 'enabled')
        min_quorum = self.govinfo['governanceminquorum']

        # the minimum quorum is calculated based on the number of masternodes
        quorum = max(min_quorum, (total_masternodes // 10))
        return quorum

    @property
    def govinfo(self):
        if (not self.governance_info):
            self.governance_info = self.rpc_command('getgovernanceinfo')
        return self.governance_info

    # governance info convenience methods
    def superblockcycle(self):
        return self.govinfo['superblockcycle']

    def last_superblock_height(self):
        height = self.rpc_command('getblockcount')
        cycle = self.superblockcycle()
        return cycle * (height // cycle)

    def next_superblock_height(self):
        return self.last_superblock_height() + self.superblockcycle()

    def is_masternode(self):
        return not (self.get_current_masternode_vin() is None)

    def is_synced(self):
        mnsync_status = self.rpc_command('mnsync', 'status')
        synced = (mnsync_status['IsSynced'] and not mnsync_status['IsFailed'])
        return synced

    def current_block_hash(self):
        height = self.rpc_command('getblockcount')
        block_hash = self.rpc_command('getblockhash', height)
        return block_hash

    def get_superblock_budget_allocation(self, height=None):
        if height is None:
            height = self.rpc_command('getblockcount')
        return Decimal(self.rpc_command('getsuperblockbudget', height))

    def next_superblock_max_budget(self):
        cycle = self.superblockcycle()
        current_block_height = self.rpc_command('getblockcount')

        last_superblock_height = (current_block_height // cycle) * cycle
        next_superblock_height = last_superblock_height + cycle

        last_allocation = self.get_superblock_budget_allocation(
            last_superblock_height)
        next_allocation = self.get_superblock_budget_allocation(
            next_superblock_height)

        next_superblock_max_budget = next_allocation

        return next_superblock_max_budget

    # "my" votes refers to the current running masternode
    # memoized on a per-run, per-object_hash basis
    def get_my_gobject_votes(self, object_hash):
        import bitgreenlib
        if not self.gobject_votes.get(object_hash):
            my_vin = self.get_current_masternode_vin()
            # if we can't get MN vin from output of `masternode status`,
            # return an empty list
            if not my_vin:
                return []

            (txid, vout_index) = my_vin.split('-')

            cmd = ['gobject', 'getcurrentvotes', object_hash, txid, vout_index]
            raw_votes = self.rpc_command(*cmd)
            self.gobject_votes[object_hash] = bitgreenlib.parse_raw_votes(
                raw_votes)

        return self.gobject_votes[object_hash]

    def is_govobj_maturity_phase(self):
        # 3-day period for govobj maturity
        maturity_phase_delta = 1662      # ~(60*24*3)/2.6
        if config.network == 'testnet':
            maturity_phase_delta = 24    # testnet

        event_block_height = self.next_superblock_height()
        maturity_phase_start_block = event_block_height - maturity_phase_delta

        current_height = self.rpc_command('getblockcount')
        event_block_height = self.next_superblock_height()

        # print "current_height = %d" % current_height
        # print "event_block_height = %d" % event_block_height
        # print "maturity_phase_delta = %d" % maturity_phase_delta
        # print "maturity_phase_start_block = %d" % maturity_phase_start_block

        return (current_height >= maturity_phase_start_block)

    def we_are_the_winner(self):
        import bitgreenlib
        # find the elected MN vin for superblock creation...
        current_block_hash = self.current_block_hash()
        mn_list = self.get_masternodes()
        winner = bitgreenlib.elect_mn(
            block_hash=current_block_hash, mnlist=mn_list)
        my_vin = self.get_current_masternode_vin()

        # print "current_block_hash: [%s]" % current_block_hash
        # print "MN election winner: [%s]" % winner
        # print "current masternode VIN: [%s]" % my_vin

        return (winner == my_vin)

    def estimate_block_time(self, height):
        import bitgreenlib
        """
        Called by block_height_to_epoch if block height is in the future.
        Call `block_height_to_epoch` instead of this method.

        DO NOT CALL DIRECTLY if you don't want a "Oh Noes." exception.
        """
        current_block_height = self.rpc_command('getblockcount')
        diff = height - current_block_height

        if (diff < 0):
            raise Exception("Oh Noes.")

        future_seconds = bitgreenlib.blocks_to_seconds(diff)
        estimated_epoch = int(time.time() + future_seconds)

        return estimated_epoch

    def block_height_to_epoch(self, height):
        """
        Get the epoch for a given block height, or estimate it if the block hasn't
        been mined yet. Call this method instead of `estimate_block_time`.
        """
        epoch = -1

        try:
            bhash = self.rpc_command('getblockhash', height)
            block = self.rpc_command('getblock', bhash)
            epoch = block['time']
        except JSONRPCException as e:
            if e.message == 'Block height out of range':
                epoch = self.estimate_block_time(height)
            else:
                print("error: %s" % e)
                raise e

        return epoch
