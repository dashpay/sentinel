import pdb
from pprint import pprint
import os
import sys
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
import models
from bitcoinrpc.authproxy import JSONRPCException


# mixin for GovObj composed classes like proposal and superblock, etc.
class GovernanceClass(object):
    def create_and_queue(self):
        # ensure unique name in govobj table...
        # ( we really need to get this redundancy out of this DB schema )
        #
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

    # TODO: ensure an object-hash exists before trying to vote
    @classmethod
    def invalid(self):
        return [obj for obj in self.select() if not obj.is_valid()]

    def get_vote_command(self, signal, outcome):
        cmd = [ 'gobject', 'vote-conf', self.governance_object.object_hash,
                signal, outcome ]
        return cmd

    # TODO: ensure an object-hash exists before trying to vote
    def vote(self, dashd, signal, outcome):
        if ( not self.governance_object or not self.governance_object.object_hash ):
            print "No governance_object hash, nothing to vote on."
            return

        vote_command = self.get_vote_command(signal, outcome)
        output = dashd.rpc_command(*vote_command)

        err_msg = ''
        try:
            detail = output.get('detail').get('dash.conf')
            result = detail.get('result')
            if 'errorMessage' in detail:
                err_msg = detail.get('errorMessage')
        except JSONRPCException as e:
            result = 'failed'
            err_msg = e.message

        # success, failed
        print "result  = [%s]" % result
        if err_msg:
            print "err_msg = [%s]" % err_msg

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


    def get_prepare_command(self):
        go = self.governance_object
        cmd = [ 'gobject', 'prepare', go.object_parent_hash,
                str(go.object_revision), str(go.object_creation_time),
                go.object_name, go.object_data ]
        return cmd

    def get_submit_command(self):
        go = self.governance_object
        cmd = [ 'gobject', 'submit', go.object_parent_hash,
                str(go.object_revision), str(go.object_creation_time),
                go.object_name, go.object_data, go.object_fee_tx ]
        return cmd

    def prepare(self, dashd):
        go = self.governance_object
        event = go.events[0]

        print "# PREPARING EVENTS FOR DASH NETWORK"
        print
        print " -- cmd : [%s]" % ' '.join(self.get_prepare_command())
        print

        try:
            collateral_tx = dashd.rpc_command(*self.get_prepare_command())
            print " -- executing prepare ... getting collateral_tx hash"
            print " -- got hash: [%s]" % collateral_tx

            go.object_fee_tx = collateral_tx
            event.prepare_time = misc.get_epoch()

            with go._meta.database.atomic():
                go.save()
                event.save()

        except JSONRPCException as e:
            event.error_time = misc.get_epoch()
            event.error_message = e.message
            event.save()
            #re-raise after capturing error message
            raise e

    # boolean -- does the object meet collateral confirmations?
    def has_collateral_confirmations(self, dashd):
        tx = dashd.rpc_command('gettransaction', govobj.object_fee_tx)
        num_bc_confirmations = tx['bcconfirmations']

        # from dash/src/governance.hL43 -- GOVERNANCE_FEE_CONFIRMATIONS
        CONFIRMATIONS_REQUIRED = 6
        print " -- confirmations: [%d]" % num_bc_confirmations
        print " -- CONFIRMATIONS_REQUIRED: [%d]" % CONFIRMATIONS_REQUIRED

        return num_bc_confirmations >= CONFIRMATIONS_REQUIRED

    def submit(self, dashd):
        go = self.governance_object
        event = go.events[0]

        print "# SUBMIT PREPARED EVENTS FOR DASH NETWORK"
        print
        print " -- submit cmd : ", ' '.join(self.get_submit_command())
        print

        if not self.has_collateral_confirmations(dashd):
            print " -- waiting for confirmations"
            return

        try:
            print " -- executing submit ... getting object hash"
            object_hash = dashd.rpc_command(*self.get_submit_command())
            print " -- got hash: [%s]" % object_hash

            event.submit_time = misc.get_epoch()
            go.object_hash = object_hash

            # save all
            with go._meta.database.atomic():
                go.save()
                event.save()

        except JSONRPCException as e:
            event.error_time = misc.get_epoch()
            event.error_message = e.message
            event.save()

            #re-raise after capturing error message
            raise e


    def serialise(self):
        import inflection
        import binascii
        import simplejson

        # 'proposal', 'superblock', etc.
        name = self._meta.name
        obj_type = inflection.singularize(name)

        return binascii.hexlify(simplejson.dumps( (obj_type, self.get_dict()) , sort_keys = True))
