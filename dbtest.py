import pdb
from pprint import pprint
import config
import re
import sys
import io
sys.path.append("lib")

from models import Event, Superblock, Proposal, GovernanceObject
from peewee import PeeweeException #, OperationalError, IntegrityError

from time import time
import govtypes

# e = Event()
# e.governance_object_id = 7
# print e.get_dict()

# check if object with name 'helloworld6' exists
#
#GovernanceObject
#object_name: helloworld6

#on = 'helloworld6'
#count = GovernanceObject.select().where(GovernanceObject.object_name == on).count()
#print "count = %d" % count

#print GovernanceObject.object_with_name_exists(on)

# select count(*) from governance_object
# where governance_object.object_name = %s

#print Event.delete().execute()
#print Superblock.delete().execute()
#print Proposal.delete().execute()
#print GovernanceObject.delete().execute()


#pw = Event.get(Event.id == 9)
#print pw.governance_object_id

# epoch = int(time())

# SELECT t1`.`id`, `t1`.`governance_object_id`, `t1`.`start_time`, `t1`.`prepare_time`, `t1`.`submit_time`, `t1`.`error_time`, `t1`.`error_message` FROM `event` AS t1 WHERE (((`t1`.`start_time` < %s) AND (`t1`.`error_time` = %s)) AND (`t1`.`prepare_time` = %s))', [1471728359, 0, 0])
#
#e = Event.get(
#    (Event.start_time < epoch ) &
#    (Event.error_time == 0) &
#    (Event.prepare_time == 0)
#)
#print(e.id)

#gobj = GovernanceObject.get()
#print gobj.object_name

#gobj.__setattr__( 'object_name' , '123456' )
#gobj.save()
#print gobj.object_name


#e = Event.get()
#print e.start_time

#e.start_time = 1471751122
#e.save()

# Event._meta.database.commit()

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
#pw_proposal = Proposal(
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
#pw_event = Event.get(Event.id == 1)
#print pw_event.governance_object_id

#gobj = GovernanceObject.get(GovernanceObject.id == 1)
#for e in gobj.event:
#  pprint(vars(e))

# ========================================================================
#parent = GovernanceObject.root()
#pprint(vars(parent))
# ========================================================================

#proposal = 1
#trigger = 2

proposal_name = "chrono-trigger-party"

gobj = GovernanceObject(
    parent_id = 0,
    object_parent_hash = 0,
    object_name = proposal_name,
    object_type = 1,
    object_revision = 1
)

pw_proposal = Proposal(
    governance_object = 42,
    proposal_name = "chrono-trigger-party",
    description_url = "https://dashcentral.com/chrono-trigger-party",
    start_epoch = 1472706000,
    end_epoch = 1475298000,
    payment_address = "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui",
    payment_amount = 7
)

#pw_proposal = Proposal.get( Proposal.id == 1 )
#gobj = pw_proposal.governance_object

#try:
#    with Event._meta.database.atomic():
#        #gobj.save()
#        pw_proposal.save()
# except OperationalError as e:
#     print "Pork Chop Sandwiches!! [%s]" % e[1]
# except IntegrityError as e:
#     print "Oh Shit! Get the fuck outta here! [%s]" % e[1]
#except PeeweeException as e:
#    print "Get the fuck out of here... you stupid idiot! [%s]" % e[1]
#    print "Fuck we're all dead! Get the fuck out!"

# print pw_proposal.name

for e in Event.select():
    print "  event id = %d" % e.id
    print "start_time = %d" % e.start_time
    print "================================="
    # pprint(vars(e))
