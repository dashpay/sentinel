import binascii
import sys

usage = "%s <hex>" % sys.argv[0]

if len(sys.argv) < 2:
    print(usage)
else:
    json = binascii.unhexlify(sys.argv[1])
    print(json)
