import os
import sys
os.environ['RPCHOST'] = 'hi'
os.environ['RPCPASSWORD'] = 'hi'
os.environ['RPCPORT'] = 'hi'
os.environ['RPCUSER'] = 'hi'
os.environ['SENTINEL_ENV'] = 'test'
os.environ['SENTINEL_CONFIG'] = os.path.normpath(os.path.join(os.path.dirname(__file__), './test_sentinel.conf'))
