import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
import base58
import hashlib
import re
from decimal import Decimal
import simplejson
import binascii
from misc import printdbg, epoch2str
import time


def is_valid_dash_address(address, network='mainnet'):
    # Only public key addresses are allowed
    # A valid address is a RIPEMD-160 hash which contains 20 bytes
    # Prior to base58 encoding 1 version byte is prepended and
    # 4 checksum bytes are appended so the total number of
    # base58 encoded bytes should be 25.  This means the number of characters
    # in the encoding should be about 34 ( 25 * log2( 256 ) / log2( 58 ) ).
    dash_version = 140 if network == 'testnet' else 76

    # Check length (This is important because the base58 library has problems
    # with long addresses (which are invalid anyway).
    if ((len(address) < 26) or (len(address) > 35)):
        return False

    address_version = None

    try:
        decoded = base58.b58decode_chk(address)
        address_version = ord(decoded[0:1])
    except:
        # rescue from exception, not a valid Dash address
        return False

    if (address_version != dash_version):
        return False

    return True


def hashit(data):
    return int(hashlib.sha256(data.encode('utf-8')).hexdigest(), 16)


# returns the masternode VIN of the elected winner
def elect_mn(**kwargs):
    current_block_hash = kwargs['block_hash']
    mn_list = kwargs['mnlist']

    # filter only enabled MNs
    enabled = [mn for mn in mn_list if mn.status == 'ENABLED']

    block_hash_hash = hashit(current_block_hash)

    candidates = []
    for mn in enabled:
        mn_vin_hash = hashit(mn.vin)
        diff = mn_vin_hash - block_hash_hash
        absdiff = abs(diff)
        candidates.append({'vin': mn.vin, 'diff': absdiff})

    candidates.sort(key=lambda k: k['diff'])

    try:
        winner = candidates[0]['vin']
    except:
        winner = None

    return winner


def parse_masternode_status_vin(status_vin_string):
    status_vin_string_regex = re.compile(r'CTxIn\(COutPoint\(([0-9a-zA-Z]+),\s*(\d+)\),')

    m = status_vin_string_regex.match(status_vin_string)

    # To Support additional format of string return from masternode status rpc.
    if m is None:
        status_output_string_regex = re.compile(r'([0-9a-zA-Z]+)-(\d+)')
        m = status_output_string_regex.match(status_vin_string)

    txid = m.group(1)
    index = m.group(2)

    vin = txid + '-' + index
    if (txid == '0000000000000000000000000000000000000000000000000000000000000000'):
        vin = None

    return vin


def create_superblock(proposals, event_block_height, budget_max, sb_epoch_time):
    from models import Superblock, GovernanceObject, Proposal
    from constants import SUPERBLOCK_FUDGE_WINDOW
    import copy

    # don't create an empty superblock
    if (len(proposals) == 0):
        printdbg("No proposals, cannot create an empty superblock.")
        return None

    budget_allocated = Decimal(0)
    fudge = SUPERBLOCK_FUDGE_WINDOW  # fudge-factor to allow for slightly incorrect estimates

    payments_list = []

    for proposal in proposals:
        fmt_string = "name: %s, rank: %4d, hash: %s, amount: %s <= %s"

        # skip proposals that are too expensive...
        if (budget_allocated + proposal.payment_amount) > budget_max:
            printdbg(
                fmt_string % (
                    proposal.name,
                    proposal.rank,
                    proposal.object_hash,
                    proposal.payment_amount,
                    "skipped (blows the budget)",
                )
            )
            continue

        # skip proposals if the SB isn't within the Proposal time window...
        window_start = proposal.start_epoch - fudge
        window_end = proposal.end_epoch + fudge

        printdbg("\twindow_start: %s" % epoch2str(window_start))
        printdbg("\twindow_end: %s" % epoch2str(window_end))
        printdbg("\tsb_epoch_time: %s" % epoch2str(sb_epoch_time))

        if (sb_epoch_time < window_start or sb_epoch_time > window_end):
            printdbg(
                fmt_string % (
                    proposal.name,
                    proposal.rank,
                    proposal.object_hash,
                    proposal.payment_amount,
                    "skipped (SB time is outside of Proposal window)",
                )
            )
            continue

        printdbg(
            fmt_string % (
                proposal.name,
                proposal.rank,
                proposal.object_hash,
                proposal.payment_amount,
                "adding",
            )
        )

        payment = {
            'address': proposal.payment_address,
            'amount': "{0:.8f}".format(proposal.payment_amount),
            'proposal': "{}".format(proposal.object_hash)
        }

        temp_payments_list = copy.deepcopy(payments_list)
        temp_payments_list.append(payment)

        # calculate size of proposed Superblock
        sb_temp = Superblock(
            event_block_height=event_block_height,
            payment_addresses='|'.join([pd['address'] for pd in temp_payments_list]),
            payment_amounts='|'.join([pd['amount'] for pd in temp_payments_list]),
            proposal_hashes='|'.join([pd['proposal'] for pd in temp_payments_list])
        )
        proposed_sb_size = len(sb_temp.serialise())

        # add proposal and keep track of total budget allocation
        budget_allocated += proposal.payment_amount
        payments_list.append(payment)

    # don't create an empty superblock
    if not payments_list:
        printdbg("No proposals made the cut!")
        return None

    # 'payments' now contains all the proposals for inclusion in the
    # Superblock, but needs to be sorted by proposal hash descending
    payments_list.sort(key=lambda k: k['proposal'], reverse=True)

    sb = Superblock(
        event_block_height=event_block_height,
        payment_addresses='|'.join([pd['address'] for pd in payments_list]),
        payment_amounts='|'.join([pd['amount'] for pd in payments_list]),
        proposal_hashes='|'.join([pd['proposal'] for pd in payments_list]),
    )
    printdbg("generated superblock: %s" % sb.__dict__)

    return sb


# convenience
def deserialise(hexdata):
    json = binascii.unhexlify(hexdata)
    obj = simplejson.loads(json, use_decimal=True)
    return obj


def serialise(dikt):
    json = simplejson.dumps(dikt, sort_keys=True, use_decimal=True)
    hexdata = binascii.hexlify(json.encode('utf-8')).decode('utf-8')
    return hexdata


def did_we_vote(output):
    from bitcoinrpc.authproxy import JSONRPCException

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
    printdbg("result  = [%s]" % result)
    if err_msg:
        printdbg("err_msg = [%s]" % err_msg)

    voted = False
    if result == 'success':
        voted = True

    # in case we spin up a new instance or server, but have already voted
    # on the network and network has recorded those votes
    m_old = re.match(r'^time between votes is too soon', err_msg)
    m_new = re.search(r'Masternode voting too often', err_msg, re.M)

    if result == 'failed' and (m_old or m_new):
        printdbg("DEBUG: Voting too often, need to sync w/network")
        voted = False

    return voted


def parse_raw_votes(raw_votes):
    votes = []
    for v in list(raw_votes.values()):
        (outpoint, ntime, outcome, signal) = v.split(':')
        signal = signal.lower()
        outcome = outcome.lower()

        mn_collateral_outpoint = parse_masternode_status_vin(outpoint)
        v = {
            'mn_collateral_outpoint': mn_collateral_outpoint,
            'signal': signal,
            'outcome': outcome,
            'ntime': ntime,
        }
        votes.append(v)

    return votes


def blocks_to_seconds(blocks):
    """
    Return the estimated number of seconds which will transpire for a given
    number of blocks.
    """
    return blocks * 2.62 * 60
