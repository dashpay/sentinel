import pdb
from pprint import pprint
import config
import re
import sys
import io
sys.path.append("lib")

from models import PeeWeeEvent, PeeWeeSuperblock, PeeWeeProposal, PeeWeeGovernanceObject
from time import time

import peewee

from governance import GovernanceObject
import govtypes

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


#e = PeeWeeEvent.get()
#print e.start_time

#e.start_time = 1471751122
#e.save()

# PeeWeeEvent._meta.database.commit()

#parent = GovernanceObject.root()
#pprint(vars(parent.governance_object))

#parent = GovernanceObject().root()
#pprint(vars(parent))

#object_type   = govtypes.proposal
#revision = 1
#proposal_name = "chrono-trigger-party"
#
#go = GovernanceObject()
#go.init(parent_id = 0, object_parent_hash = 0, object_name = proposal_name, object_type = object_type, object_revision = 1)
#goid = go.save()
##pprint(vars(go.governance_object))
#
#url = "https://dashcentral.com/chrono-trigger-party"
#payment_address = "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui"
#payment_amount = 7
#
#pw_proposal = PeeWeeProposal(
#    start_epoch = 1472706000,
#    end_epoch = 1475298000,
#    governance_object_id = goid,
#    proposal_name = proposal_name,
#    description_url = url,
#    payment_address = payment_address,
#    payment_amount = payment_amount
#)
#pprint(vars(pw_proposal))
#
#pw_proposal.save()
#
#pprint(vars(pw_proposal))

#proposal_name = "chrono-trigger-party"
#pw_event = PeeWeeEvent.get(PeeWeeEvent.id == 1)
#print pw_event.governance_object_id

#gobj = PeeWeeGovernanceObject.get(PeeWeeGovernanceObject.id == 1)
#for e in gobj.event:
#  pprint(vars(e))

# ========================================================================


### #proposal = 1
### #trigger = 2
###
### proposal_name = "chrono-trigger-party"
###
### gobj = PeeWeeGovernanceObject(
###     parent_id = 0,
###     object_parent_hash = 0,
###     object_name = proposal_name,
###     object_type = 1,
###     object_revision = 1
### )
###
### pw_proposal = PeeWeeProposal(
###     governance_object = gobj,
###     proposal_name = "chrono-trigger-party",
###     description_url = "https://dashcentral.com/chrono-trigger-party",
###     start_epoch = 1472706000,
###     end_epoch = 1475298000,
###     payment_address = "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui",
###     payment_amount = 7
### )
###
### pw_proposal = PeeWeeProposal.get( PeeWeeProposal.id == 1 )
### gobj = pw_proposal.governance_object
### the_hex = gobj.object_data
### print "the_hex = %s" % the_hex
###
### ##try:
### ##    with PeeWeeEvent._meta.database.atomic():
### ##        gobj.save()
### ##        pw_proposal.save()
### ##except peewee.OperationalError:
### ##    print "Pork Chop Sandwiches!!"
### ##except peewee.IntegrityError:
### ##    print "Oh Shit! Get the fuck outta here!"
### ##except:
### ##    print "Get the fuck out of here... you stupid idiot!"
### ##    print "Fuck we're all dead! Get the fuck out!"
###
### # pprint(vars(pw_proposal))

parent = PeeWeeGovernanceObject.root()

pprint(vars(parent))
