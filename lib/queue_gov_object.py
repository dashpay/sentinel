import pdb
from pprint import pprint
import os
import sys
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
import models
from bitcoinrpc.authproxy import JSONRPCException
import misc
import re

# mixin for GovObj composed classes like proposal and superblock, etc.
class GovernanceClass(object):
    def create_with_govobj(self):
        govobj = models.GovernanceObject(
            object_name = self.name,
            object_type = self.govobj_type,
        )
        self.governance_object = govobj

        # atomic write for both objects, 1:1 relationship
        with models.BaseModel._meta.database.atomic():
            govobj.save()
            self.save()

    def vote_validity(self, dashd):
        if self.is_valid(dashd):
            print "Voting valid! %s: %d" % (self.__class__.__name__, self.id)
            self.vote(dashd, 'valid', 'yes')
        else:
            print "Voting INVALID! %s: %d" % (self.__class__.__name__, self.id)
            self.vote(dashd, 'valid', 'no')

    def get_vote_command(self, signal, outcome):
        cmd = [ 'gobject', 'vote-conf', self.governance_object.object_hash,
                signal, outcome ]
        return cmd

    def voted_on(self, **kwargs):
        signal  = kwargs.get('signal', None)
        outcome = kwargs.get('outcome', None)

        query = self.governance_object.votes

        if signal:
            query = query.where(models.Vote.signal == signal)

        if outcome:
            query = query.where(models.Vote.outcome == outcome)

        count = query.count()
        return count

    def vote(self, dashd, signal, outcome):
        go = self.governance_object

        # At this point, will probably never reach here. But doesn't hurt to
        # have an extra check just in case objects get out of sync (people will
        # muck with the DB).
        if ( not go or go.object_hash == '0' or not misc.is_hash(go.object_hash)):
            print "No governance_object hash, nothing to vote on."
            return

        # TODO: ensure Signal, Outcome are valid options for dashd
        vote_command = self.get_vote_command(signal, outcome)
        print ' '.join(vote_command)
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

        voted = False
        if result == 'success':
            voted = True

        # in case we spin up a new instance or server, but have already voted
        # on the network and network has recorded those votes
        m = re.match(r'^time between votes is too soon', err_msg)
        if result == 'failed' and m:
            print "DEBUG: failed, but marking as voted..."
            voted = True

        if voted:
            # TODO: ensure signal, outcome exist in lookup table or raise exception
            v = models.Vote(
                governance_object=self.governance_object,
                signal=models.Signal.get(models.Signal.name == signal),
                outcome=models.Outcome.get(models.Outcome.name == outcome),
                object_hash=go.object_hash,
            )
            v.save()

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

    # boolean -- does the object meet collateral confirmations?
    def submit(self, dashd):
        go = self.governance_object

        # don't attempt to submit a superblock unless a masternode
        # note: will probably re-factor this, this has code smell
        my_vin = dashd.get_current_masternode_vin()
        if (isinstance(self, models.Superblock) and (my_vin == None)):
            print "Not a masternode. Only masternodes may submit superblocks."
            return

        print " -- submit cmd : ", ' '.join(self.get_submit_command())
        print
        print " -- executing submit ... getting object hash"
        object_hash = dashd.rpc_command(*self.get_submit_command())
        print " -- got hash: [%s]" % object_hash

        go.object_hash = object_hash
        go.save()

    def serialise(self):
        import inflection
        import binascii
        import simplejson

        # 'proposal', 'superblock', etc.
        name = self._meta.name
        obj_type = inflection.singularize(name)

        return binascii.hexlify(simplejson.dumps( (obj_type, self.get_dict()) , sort_keys = True))

    @classmethod
    def serialisable_fields(self):
        # Python is so not very elegant...
        pk_column  = self._meta.primary_key.db_column
        fk_columns = [ fk.db_column for fk in self._meta.rel.values() ]
        do_not_use = [ pk_column ]
        do_not_use.extend(fk_columns)
        do_not_use.append('object_hash')
        fields_to_serialise = self._meta.columns.keys()

        for field in do_not_use:
            if field in fields_to_serialise:
                fields_to_serialise.remove(field)

        return fields_to_serialise

    def get_dict(self):
        dikt = {}

        for field_name in self.serialisable_fields():
            dikt[ field_name ] = getattr( self, field_name )

        return dikt
