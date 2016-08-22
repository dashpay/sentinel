from pprint import pprint
import config
import re
import sys
import io
sys.path.append("lib")

from models import PeeWeeEvent, PeeWeeSuperblock, PeeWeeProposal, PeeWeeGovernanceObject
from time import time

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


#pw = PeeWeeEvent.get(PeeWeeEvent.id == 9)
#print pw.governance_object_id

# epoch = int(time())

# SELECT t1`.`id`, `t1`.`governance_object_id`, `t1`.`start_time`, `t1`.`prepare_time`, `t1`.`submit_time`, `t1`.`error_time`, `t1`.`error_message` FROM `event` AS t1 WHERE (((`t1`.`start_time` < %s) AND (`t1`.`error_time` = %s)) AND (`t1`.`prepare_time` = %s))', [1471728359, 0, 0])
#
#e = PeeWeeEvent.get(
#    (PeeWeeEvent.start_time < epoch ) &
#    (PeeWeeEvent.error_time == 0) &
#    (PeeWeeEvent.prepare_time == 0)
#)
#print(e.id)

#gobj = PeeWeeGovernanceObject.get()
#print gobj.object_name

#gobj.__setattr__( 'object_name' , '123456' )
#gobj.save()
#print gobj.object_name


e = PeeWeeEvent.get()
print e.start_time

#e.start_time = 1471751122
#e.save()

# PeeWeeEvent._meta.database.commit()


