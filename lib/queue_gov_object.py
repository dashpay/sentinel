import os
import sys
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
import models


# mixin for GovObj composed classes like proposal and superblock, etc.
class GovernanceClass(object):
    def create_and_queue(self):
        # ensure unique name in govobj table...
        # ( we really need to get this redundancy out of this DB schema )
        #
        # actually, since the enhanced DB schema enforces unique names on the
        # individual subobj tables, this shouldn't be necessary. no defensive
        # coding, just try/except and pass error thru
        #
        # if GovernanceObject.object_with_name_exists(object_name):
        #     print "governance object with that name already exists"
        #     return

        # requirements: mix'ed in object must have 'name' and 'govobj_type'
        # properties

        govobj = models.GovernanceObject(
            object_name = self.name,
            object_type = self.govobj_type,
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

    def get_vote_command(self, signal, outcome):
        cmd = [ 'gobject', 'vote-conf', self.governance_object.object_hash,
                signal, outcome ]
        return cmd

    def vote(self, dashd, signal, outcome):
        vote_command = self.get_vote_command(signal, outcome)
        output = dashd.rpc_command(vote_command)
        # TODO: do we need to track our own votes?
        # self.object_status = 'VOTED'
        # self.save()

    def list(self):
        dikt = {
            "Name": self.name,
            "DataHex": self.governance_object.object_data,
            "Hash": self.governance_object.object_hash,
            "CollateralHash": self.governance_object.object_fee_tx,
            "AbsoluteYesCount": self.governance_object.absolute_yes_count,
            "YesCount": self.governance_object.yes_count,
            "NoCount": self.governance_object.no_count,
            "AbstainCount": self.governance_object.abstain_count,
        }

        # return a dict similar to dashd "gobject list" output
        return { self.name: dikt }


    def serialize(self):
        import inflection
        import binascii
        import simplejson
        dashd_type = inflection.singularize(self._meta.name)
        if dashd_type == 'superblock':
            dashd_type = 'trigger'

        return binascii.hexlify(simplejson.dumps( (dashd_type, self.get_dict()) , sort_keys = True))
