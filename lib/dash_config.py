import sys
import os
import io
import re

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "lib"))
from misc import printdbg


class DashConfig:
    @classmethod
    def slurp_config_file(self, filename):
        # read dash.conf config but skip commented lines
        f = io.open(filename)
        lines = []
        for line in f:
            if re.match(r"^\s*#", line):
                continue
            lines.append(line)
        f.close()

        # data is dash.conf without commented lines
        data = "".join(lines)

        return data

    @classmethod
    def get_rpc_creds(self, data):
        # get rpc info from dash.conf
        match = re.findall(r"rpc(user|password|port)=(.*?)$", data, re.MULTILINE)

        # python >= 2.7
        creds = {key: value for (key, value) in match}

        # determine default rpc port from testnet= setting in dash.conf
        network = "mainnet"
        testnet_value = re.search(r"testnet=(.*?)$", data, re.MULTILINE)
        if testnet_value:
            capture = testnet_value[1].strip()
            try:
                if int(capture) != 0:
                    network = "testnet"
            except ValueError as e:
                network = "testnet"

        # standard Dash defaults...
        default_port = 9998 if (network == "mainnet") else 19998

        # use default port for network if not specified in dash.conf
        if not ("port" in creds):
            creds["port"] = default_port

        # convert to an int if taken from dash.conf
        creds["port"] = int(creds["port"])

        # return a dictionary with RPC credential key, value pairs
        return creds

    @classmethod
    def tokenize(self, filename):
        tokens = {}
        try:
            data = self.slurp_config_file(filename)
            match = re.findall(r"(.*?)=(.*?)$", data, re.MULTILINE)
            tokens = {key: value for (key, value) in match}
        except IOError as e:
            printdbg("[warning] error reading config file: %s" % e)

        return tokens
