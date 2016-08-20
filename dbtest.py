from pprint import pprint
import config
import re
import sys
import io
sys.path.append("lib")
from models import PeeWeeEvent, PeeWeeSuperblock, PeeWeeProposal, PeeWeeGovernanceObject
from datetime import datetime, date, time

# e = PeeWeeEvent()
# e.governance_object_id = 7
# print e.get_dict()

# check if object with name 'helloworld6' exists
#
#PeeWeeGovernanceObject
#object_name: helloworld6

#on = 'helloworld6'
#count = PeeWeeGovernanceObject.select().where(PeeWeeGovernanceObject.object_name == on).count()
#print "count = %d" % count

#print PeeWeeGovernanceObject.object_with_name_exists(on)

# select count(*) from governance_object
# where governance_object.object_name = %s

#print PeeWeeEvent.delete().execute()
#print PeeWeeSuperblock.delete().execute()
#print PeeWeeProposal.delete().execute()
#print PeeWeeGovernanceObject.delete().execute()

