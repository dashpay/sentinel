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

    # @classmethod
    # def create(self, *args, **kwargs):
    #     # pdb.set_trace()
    #
    #     print "hi!!!! HEERRR"
    #     # TODO: Loop thru the kwargs & find a governance_object.
    #     # if one doesn't exist, create a default one with correct name, type.
    #     # then loop thru the KWARGS looking at govobj-specific keywords and set those in the new govobj first.
    #     # kwargs
    #
    #     # for k, v in kwargs.iteritems():
    #     #     print "kwargs[%s] = %s" % (k, v)
    #
    #     goid = None
    #
    #
    #     # if an un-saved governance_object is passed in, then
    #     try:
    #         go = kwargs['governance_object']
    #         if not go.id:
    #             go.save()
    #         goid = go.id
    #     except KeyError as e:
    #         pass
    #
    #     goid = kwargs.get('governance_object_id', None)
    #
    #     try:
    #         goid = goid or kwargs['governance_object_id']
    #     except KeyError as e:
    #         pass
    #
    #     if not goid:
    #         try:
    #             go = models.GovernanceObject(object_name=kwargs['name'], object_type=self.govobj_type)
    #             go.save()
    #             kwargs['governance_object_id'] = go.id
    #         except Exception as e:
    #             print "error: %s" % e
    #             pass
    #
    #     # pdb.set_trace()
    #     super(GovernanceClass, self).create(*args, **kwargs)
    #     print "hi!!!! LEEEEEVVVINGGG!!!!"

    # TODO: ensure an object-hash exists before trying to vote
    @classmethod
    def invalid(self):
        return [obj for obj in self.select() if not obj.is_valid()]

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

    # TODO: ensure an object-hash exists before trying to vote
    def vote(self, dashd, signal, outcome):
        go = self.governance_object

        # At this point, will probably never reach here. But doesn't hurt to
        # have an extra check just in case objects get out of sync or ppl start
        # messing with the DB.
        if ( not go or go.object_hash == '0' or go.object_hash == '' or not misc.is_hash(go.object_hash)):
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
            v = models.Vote(governance_object=self.governance_object,
                            signal=models.Signal.get(models.Signal.name == signal),
                            outcome=models.Outcome.get(models.Outcome.name == outcome))
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


    def get_submit_command(self):
        go = self.governance_object
        cmd = [ 'gobject', 'submit', go.object_parent_hash,
                str(go.object_revision), str(go.object_creation_time),
                go.object_name, go.object_data, go.object_fee_tx ]
        return cmd

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
