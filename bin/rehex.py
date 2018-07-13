import simplejson
import binascii
import sys
import pdb
from pprint import pprint
import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../lib')))
import machinecoinlib
# ============================================================================
usage = "%s <hex>" % sys.argv[0]

obj = None
if len(sys.argv) < 2:
    print(usage)
    sys.exit(1)
else:
    obj = machinecoinlib.deserialise(sys.argv[1])

pdb.set_trace()
1
