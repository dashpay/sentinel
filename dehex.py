from pprint import pprint
import config
import re
import sys
import io
sys.path.append("lib")
import binascii

hex = sys.argv[1]

json = binascii.unhexlify( hex )

print json

