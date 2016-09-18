import pdb
from pprint import pprint
import sys, os
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
import base58
import hashlib
import re
from decimal import Decimal
import simplejson
import binascii
from peewee import DoesNotExist

def is_valid_dash_address( address, network = 'mainnet' ):
    # Only public key addresses are allowed
    # A valid address is a RIPEMD-160 hash which contains 20 bytes
    # Prior to base58 encoding 1 version byte is prepended and
    # 4 checksum bytes are appended so the total number of
    # base58 encoded bytes should be 25.  This means the number of characters
    # in the encoding should be about 34 ( 25 * log2( 256 ) / log2( 58 ) ).
    dash_version = 140 if network == 'testnet' else 76

    # Check length (This is important because the base58 library has problems
    # with long addresses (which are invalid anyway).
    if ( ( len( address ) < 26 ) or ( len( address ) > 35 ) ):
        return False

    address_version = None

    try:
        decoded = base58.b58decode_chk(address)
        address_version = ord(decoded[0])
    except TypeError as e:
        # rescue from exception, not a valid Dash address
        return False

    if ( address_version != dash_version ):
        return False

    return True


def hashit( data ):
    return int( hashlib.sha256(data).hexdigest(), 16 )

# returns the masternode VIN of the elected winner
def elect_mn(**kwargs):
    current_block_hash = kwargs['block_hash']
    mn_list = kwargs['mnlist']

    # filter only enabled MNs
    enabled = [mn for mn in mn_list if mn.status == 'ENABLED']

    # TODO: need to use an offset, e.g. 10 blocks or something -- discuss w/Evan.
    block_hash_hash = hashit(current_block_hash)

    candidates = []
    for mn in enabled:
        mn_vin_hash = hashit( mn.vin )
        diff = mn_vin_hash - block_hash_hash
        absdiff = abs( diff )
        candidates.append({ 'vin': mn.vin, 'diff': absdiff })

    candidates.sort( key = lambda k: k['diff'] )

    try:
        winner = candidates[0]['vin']
    except (IndexError, AttributeError) as e:
        winner = None

    return winner


def parse_masternode_status_vin(status_vin_string):
    status_vin_string_regex = re.compile( 'CTxIn\(COutPoint\(([0-9a-zA-Z]+),\\s*(\d+)\),' )

    m = status_vin_string_regex.match( status_vin_string )
    txid = m.group(1)
    index = m.group(2)

    vin = txid + '-' + index
    if (txid == '0000000000000000000000000000000000000000000000000000000000000000'):
        vin = None

    return vin


# create superblock logic -- probably need a join table for proposal, superblock linkage
def create_superblock( dashd, proposals, event_block_height ):
    from models import Superblock, GovernanceObject, Proposal
    import dashlib

    # don't create an empty superblock
    if ( len(proposals) == 0 ):
        print "No proposals!"
        return None

    budget_allocated = Decimal(0)
    budget_max       = dashd.get_superblock_budget_allocation(event_block_height)

    print "  IN create_superblock"
    print "    current height: %d" % dashd.rpc_command('getblockcount')
    print "event_block_height: %d" % event_block_height
    print "       budget_max : %d" % budget_max
    print " "

    # TODO: probably use a sub-table to link proposals for RI
    payments = []
    for proposal in proposals:
        # fmt_string = "name: %s , rank: %4d , amount: %s <= %s"
        fmt_string = "name: %s, rank: %4d, hash: %s, amount: %s <= %s"

        # skip proposals that are too expensive...
        if (budget_allocated + proposal.payment_amount) > budget_max:
            print fmt_string % (
                proposal.name,
                proposal.rank,
                proposal.object_hash,
                proposal.payment_amount,
                "skipped (blows the budget)",
            )
            continue

        print fmt_string % (
            proposal.name,
            proposal.rank,
            proposal.object_hash,
            proposal.payment_amount,
            "adding",
        )

        # else add proposal and keep track of total budget allocation
        budget_allocated += proposal.payment_amount

        # TODO: probably use a sub-table to link proposals for RI
        payment = { 'address': proposal.payment_address,
                    'amount': proposal.payment_amount }
        payments.append( payment )

    # don't create an empty superblock
    if not payments:
        print "No proposals made the cut!"
        return None

    # deterministic superblocks can't have random names
    sbname = "sb" + str(event_block_height)

    # TODO: separate table for payments, in a specified order. Will enforce RI
    # in the DB schema.
    sb = Superblock(
        name = sbname,
        event_block_height = event_block_height,
        payment_addresses = '|'.join([str(pd['address']) for pd in payments]),
        payment_amounts   = '|'.join([str(pd['amount' ]) for pd in payments]),
    )

    return sb


# TODO: stick this somewhere that makes more sense
DASHD_GOVOBJ_TYPES = {
    'proposal': 1,
    'superblock': 2,
}

# shims 'til we can fix the dashd side
def SHIM_serialise_for_dashd(sentinel_hex):
    # unpack
    obj = deserialise(sentinel_hex)

    # shim for dashd
    govtype = obj[0]

    # add 'type' attribute
    obj[1]['type'] = DASHD_GOVOBJ_TYPES[govtype]

    # superblock => "trigger" in dashd
    if govtype == 'superblock':
        obj[0] = 'trigger'

    # dashd expects an array (even though there is only a 1:1 relationship between govobj->class)
    obj = [obj]

    # re-pack
    dashd_hex = serialise(obj)
    return dashd_hex

# shims 'til we can fix the dashd side
def SHIM_deserialise_from_dashd(dashd_hex):
    # unpack
    obj = deserialise(dashd_hex)

    # shim from dashd
    # only one element in the array...
    obj = obj[0]

    # extract the govobj type
    govtype = obj[0]

    # superblock => "trigger" in dashd
    if govtype == 'trigger':
        obj[0] = govtype = 'superblock'

    # remove redundant 'type' attribute
    if 'type' in obj[1]:
        del obj[1]['type']

    # re-pack
    sentinel_hex = serialise(obj)
    return sentinel_hex

# convenience
def deserialise(hexdata):
    json = binascii.unhexlify(hexdata)
    obj  = simplejson.loads(json, use_decimal=True)
    return obj

def serialise(dikt):
    json = simplejson.dumps(dikt, sort_keys=True, use_decimal=True)
    hexdata = binascii.hexlify(json)
    return hexdata

def did_we_vote(output):
    # sentinel
    voted = False
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

    return voted
