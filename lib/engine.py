
import dashd

VOTE_OUTCOME_NONE     =0
VOTE_OUTCOME_YES      =1
VOTE_OUTCOME_NO       =2
VOTE_OUTCOME_ABSTAIN  =3

VOTE_ACTION_NONE              =  0
VOTE_ACTION_FUNDING           =  1 #SIGNAL TO FUND GOVOBJ
VOTE_ACTION_VALID             =  2 #SIGNAL GOVOBJ IS VALID OR NOT
VOTE_ACTION_UPTODATE          =  3 #SIGNAL ALL REQUIRED INFORMATION IS UP-TO-DATE (PROJECTS/MILESTONES/REPORTS)
VOTE_ACTION_DELETE            =  4 #SIGNAL TO DELETE NODE AND CHILDREN FROM SYSTEM
VOTE_ACTION_CLEAR_REGISTERS   =  5 #SIGNAL TO CLEAR REGISTER DATA (DASHDRIVE or other outer-storage implementations)
VOTE_ACTION_ENDORSED          =  6 #SIGNAL GOVOBJ IS ENDORSED BY REVIEW COMMITTEES


class Engine():

	def __init__():
		pass

	def get_object(self, args):

		"""
			convert parameters into json object representing the governance object
			create converter for json object to register conversion, per version type

			perform the following:
				- find hash parent by ownership
				- look in database for most recent revision, check instruction validity
				- add to event table

			crontab will pick this up in scripts/events.sh
		"""

		for each i in args:

	def update_governance_items():
		ret = cmd("governance list")

		"""
			loop through records update governance_object

		for items in ret:
			process_new_record(rec)

		"""

	" unserialize object, load into class "
	def load_governance_object(rec):
		pass

	" submit the vote to the network"
	def vote(obj, action, outcome):
		pass

engine = Engine()
