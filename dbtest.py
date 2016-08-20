from pprint import pprint
import config
import re
import sys
import io
sys.path.append("lib")
from models import PeeWeeEvent, PeeWeeSuperblock, PeeWeeProposal
from datetime import datetime, date, time


e = PeeWeeEvent()
e.governance_object_id = 7

# pprint(dir(e))
# print e.__getattribute__( 'governance_object_id' )

print e.get_dict()


