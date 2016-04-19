

class User:
    """A simple dash user"""
    userid = 0 #incremental

    def __init__(self, userid):

    	if userid > Users.get_last_uid(): return

    	load(userid)

    def load(self, userid):
    	q = sql("select * from datatable where userid=" userid)

    	#load it

    	pass

    def create(self, first, last, address1, address2, city, state, country):
        userid = Users.get_last_uid() + 1

        #insert into table

# Users is a Singleton/SingletonPattern.py

class Users:
    class __Users:
    	highest_uid = 0

        def __init__(self, arg):
            self.val = arg
        def __str__(self):
            return repr(self) + self.val
        def get_last_uid(self):
        	return highest_uid
        def get_new_user(self):
        	retu

    instance = None
    def __init__(self, arg):
        if not Users.instance:
            Users.instance = Users.__Users(arg)
        else:
            Users.instance.val = arg
    def __getattr__(self, name):
        return getattr(self.instance, name)

x = Users()
print(x)