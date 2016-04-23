# sentinel-cli [command] 

All basic commands for creating objects:

## Managers: Setting Up Employment 
<pre>
    # Create a manager
    --create="user" --name="user-maria-2016" --revision=1 --subclass="manager" --dash_monthly=233.32 --first_name="maria" --last_name="johnson"
    --address1="123 w. main ave" --address2="#123" --city="?" --state="?" --country="US"

    # Create the employement relationship between parties
    --create=relationship --subclass="offer-of-employment" -to_user="maria" --ask="500 DASH" #network executes
    --create=relationship --subclass="request-of-employment" -to_user="network" --ask="500 DASH" #network executes

    # creating a relationship takes a two-way connection, if either party deletes a connection the employment is abandoned
    #  -- any of these will cause termination of employment, if employee doesn't find a new manager within 15 days
    --delete=relationship --subclass="offer-of-employment" --to_user="maria" --bid="500 DASH" #maria executes

    # coming to terms
    #  -- employment is a bid/ask, amounts much match and can be revised
    #  -- sib bids 4500 DASH 
    #  -- maria bids 2200 DASH
    #  -- sib amends 3400 DASH
    --amend=relationship --subclass="offer-of-employment" --to_user="sib" --bid="3400 DASH" #maria executes
</pre>

## Employee: Setting Up Employment
<pre>
    # Create the employement relationship between parties
    --create=relationship --subclass="offer-of-employment" --to_user="sib" --bid="4500 DASH" #maria executes
    --create=relationship --subclass="request-of-employment" -to_user="maria" --ask="2200 DASH" #sib executes
    --create=relationship --subclass="offer-of-employment-secondary" --to_user="sib" #robert executes
    --create=relationship --subclass="request-of-employment-secondary" --to_user="robert" #sib executes

    # creating a relationship takes a two-way connection, if either party deletes a connection the employment is abandoned
    #  -- any of these will cause termination of employment, if employee doesn't find a new manager within 15 days
    --delete=relationship --subclass="offer-of-employment" --to_user="sib" --bid="4500 DASH" #maria executes

    # coming to terms
    #  -- employment is a bid/ask, amounts much match and can be revised
    #  -- sib bids 4500 DASH 
    #  -- maria bids 2200 DASH
    #  -- sib amends 3400 DASH
    --amend=relationship --subclass="offer-of-employment" --to_user="sib" --bid="3400 DASH" #maria executes
</pre>

## Expenses: Get reimbursed for something you're doing/did
<pre>
    # Create the employement relationship between parties
    --create=expense --subclass="travel" --to_user="maria" --bid="25.234 DASH" --desc="First Class Plane Ticket!"  #sib executes
    --create=expense --subclass="travel" --to_user="sib" --bid="17.234 DASH" --desc="Not on our money."  #maria executes

    # coming to terms
    #  -- employment is a bid/ask, amounts much match and can be revised
    #  -- sib bids 25.34 DASH 
    #  -- maria bids 17.234 DASH (network doesn't pay first class flights)
    #  -- sib bids 17.234 DASH (paid next month)
    --create=expense --subclass="travel" --to_user="maria" --bid="25.234 DASH" --desc="First Class Plane Ticket!"  #sib executes
</pre>
