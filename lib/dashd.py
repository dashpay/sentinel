#!/usr/bin/env python

"""
Dashd interface
----

"""

import os
import config
import subprocess
import json
import sys

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

class DashDaemon():
    def __init__(self, **kwargs):
        host = kwargs.get('host', '127.0.0.1')
        user = kwargs.get('user')
        password = kwargs.get('password')
        port = kwargs.get('port')

        creds = (user, password, host, port)
        self.rpc_connection = AuthServiceProxy("http://{0}:{1}@{2}:{3}".format(*creds))

    def rpc_command(params):
        return rpc_connection.getattr(params[0])(params[1:])


class CTransaction():
    tx = {}

    def __init__(self):
        tx = {
            "bcconfirmations" : 0
        }
        return None

    def load(self, txid):
        result = rpc_command("gettransaction " + txid)

        try:
            obj = json.loads(result)
            if obj:
                self.tx = obj
                return True
            else:
                print "error loading tx"
                return False
        except:
            print "Unexpected error:", sys.exc_info()[0]
            print
            print "dashd result:", result
            print
            return False

    def get_hash(self):
        return None

    def get_confirmations(self):
        return self.tx["bcconfirmations"]
