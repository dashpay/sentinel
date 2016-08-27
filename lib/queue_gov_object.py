import os
import sys
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
import models

# mixin for GovObj sub-objects like proposal and superblock, etc.
class QueueGovObject(object):
    def create_and_queue(self, the_type):
        # This "type" system reeks of bad design and I need to think of a better
        # way to implement this in the DB and hwo to work w/it...
        #
        # for now, will leave as-is 'til we can come up w/something

        # ( we really need to get this redundancy out of this DB schema )
        #
        # actually, since the enhanced DB schema enforces unique names on the
        # individual subobj tables, this shouldn't be necessary. no defensive
        # coding, just try/except and pass error thru
        #
        # ensure unique name in govobj table...
        # if GovernanceObject.object_with_name_exists(object_name):
        #     print "governance object with that name already exists"
        #     return

        # requirements: mix'ed in object must have 'name' property

        govobj = models.GovernanceObject(
            object_name = self.name,
            object_type = the_type,
        )

        self.governance_object = govobj

        # CREATE EVENT TO TALK TO DASHD / PREPARE / SUBMIT OBJECT
        event = models.Event(governance_object = govobj)

        # do not try/catch here, let it bubble thru...

        # atomic write for all 3 objects, alles oder nichts
        with models.Event._meta.database.atomic():
            govobj.save()
            event.save()
            self.save()

        return
