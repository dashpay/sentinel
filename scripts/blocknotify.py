#!/usr/bin/env python

import json
import dashd

import sys
sys.path.append("lib")

from govobj import GovernanceObject


"""
    - this script is ran ~2.5/minutes and processes updates to the governance system 

"""

difflist = json.loads(dashd.cmd("governance diff"))
for item in difflist:
	obj = GovernanceObject(item)
	obj.save()

	if obj.is_valid():
		obj.vote(VOTE_ACTION_VALID, VOTE_OUTCOME_NO)
pass