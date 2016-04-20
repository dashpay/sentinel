#!/usr/bin/env python

"""
	- look through events table, process what we're suppose to do
	- can include building fee transactions, submitting govobjs to the network

"""

import sys
sys.path.append("../lib")

import mysql 

from govobj import GovernanceObject
import events
import dashd

def __prepare():
	sql = "select * from events where prepare_time is NULL limit 1"

	# prepare fee_tx, store into govobj

	"""
	obj = GovernanceObject(item)
	prepare_cmd = obj.get_dashd_command("prepare")
	dashd.cmd(prepare_cmd)
	"""

	# update record


def __submit():
	sql = "select * from events where prepare_time != NULL and submit_time is NULL limit 1"

	# submit to network

	"""
	obj = GovernanceObject(item)
	submit_cmd = obj.get_dashd_command("submit")
	dashd.cmd(submit_cmd)
	"""

	# update records

	pass


def process():
	__prepare()
	__submit()


if __name__ == '__main__':
	Process()