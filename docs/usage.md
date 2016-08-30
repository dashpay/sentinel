# sentinel-cli [command] 

<pre>
All basic commands for creating objects:
</pre>

## Managers: Setting Up Employment 
<pre>
    # Create a manager
    --create="user" --name="user-terra-2016" --revision=1 --subclass="manager" --dash_monthly=233.32 --first_name="terra" --last_name="johnson"
    --address1="123 w. main ave" --address2="#123" --city="?" --state="?" --country="US"

    # Create the employement relationship between parties
    --create=relationship --subclass="offer-of-employment" -to_user="terra" --ask="500 DASH" #network executes
    --create=relationship --subclass="request-for-employment" -to_user="network" --ask="500 DASH" #network executes

    # creating a relationship takes a two-way connection, if either party deletes a connection the employment is abandoned
    #  -- any of these will cause termination of employment, if employee doesn't find a new manager within 15 days
    --delete=relationship --subclass="offer-of-employment" --to_user="terra" --bid="500 DASH" #terra executes

    # coming to terms
    #  -- employment is a bid/ask, amounts much match and can be revised
    #  -- cid bids 4500 DASH 
    #  -- terra bids 2200 DASH
    #  -- cid amends 3400 DASH
    --amend=relationship --subclass="offer-of-employment" --to_user="cid" --bid="3400 DASH" #terra executes
</pre>

## Employee: Setting Up Employment
<pre>
    # Create the employement relationship between parties
    --create=relationship --subclass="offer-of-employment" --to_user="cid" --bid="4500 DASH" #terra executes
    --create=relationship --subclass="request-for-employment" -to_user="terra" --ask="2200 DASH" #cid executes
    --create=relationship --subclass="offer-of-employment-secondary" --to_user="cid" #robert executes
    --create=relationship --subclass="request-for-employment-secondary" --to_user="robert" #cid executes

    # creating a relationship takes a two-way connection, if either party deletes a connection the employment is abandoned
    #  -- any of these will cause termination of employment, if employee doesn't find a new manager within 15 days
    --delete=relationship --subclass="offer-of-employment" --to_user="cid" --bid="4500 DASH" #terra executes

    # coming to terms
    #  -- employment is a bid/ask, amounts much match and can be revised
    #  -- cid bids 4500 DASH 
    #  -- terra bids 2200 DASH
    #  -- cid amends 3400 DASH
    --amend=relationship --subclass="offer-of-employment" --to_user="cid" --bid="3400 DASH" #terra executes
</pre>

## Expenses: Get reimbursed for something you're doing/did
<pre>
    # Create the employement relationship between parties
    --create=expense --subclass="travel" --to_user="terra" --bid="25.234 DASH" --desc="First Class Plane Ticket!"  #cid executes
    --create=expense --subclass="travel" --to_user="cid" --bid="17.234 DASH" --desc="Not on our money."  #terra executes

    # coming to terms
    #  -- employment is a bid/ask, amounts much match and can be revised
    #  -- cid bids 25.34 DASH 
    #  -- terra bids 17.234 DASH (network doesn't pay first class flights)
    #  -- cid bids 17.234 DASH (paid next month)
    --create=expense --subclass="travel" --to_user="terra" --bid="25.234 DASH" --desc="First Class Plane Ticket!"  #cid executes
</pre>

## To fund projects and work on them, we can create new types of objects with built in rewards
## structure is a bid/ask system for creating projects and executing them. The network will decide the proposalor by matching 
<pre>
    # Create the employement relationship between parties
    --create=project --subclass="software" --name="core-12.1x" --users="terra:cyan:cid:locke" --bid_bounties="250:0:0" --desc="release 12.1"  #cid executes
    --create=project --subclass="software" --name="core-12.1x" --users="terra:cyan:cid:locke" --ask_bounties="150:0:0" --desc="release 12.1"  #terra executes
</pre>

## To release bounties, masternodes must manually tell the network the project is complete
<pre>
    --vote-times=22 --vote-type="release-bounty1" --vote-outcome="yes" --name="core-12.1x"
</pre>


