
import calendar
import time
import argparse
import sys
sys.path.append("../")
sys.path.append("../lib")
sys.path.append("../scripts")

import mysql 
from misc import *
import event

class Event:
    event = {}
    def __init__(self):
        pass

    def create_new(self, last_id):
        self.event["governance_object_id"] = last_id
        self.event["start_time"] = calendar.timegm(time.gmtime())
        self.event["prepare_time"] = 'NULL'
        self.event["submit_time"] = 'NULL'

    def load(self, record_id):
        sql = """
            select
                id,
                governance_object_id,
                start_time,
                prepare_time,
                submit_time
            from event where 
                id = %s """ % record_id

        mysql.db.query(sql)
        res = mysql.db.store_result()
        row = res.fetch_row()
        if row:
            print row[0]
            (self.event["id"], self.event["governance_object_id"], self.event["start_time"],
                self.event["prepare_time"], self.event["submit_time"]) = row[0]
            print "loaded event successfully"

            if self.event["start_time"] == None: self.event["start_time"] = 'NULL'
            if self.event["submit_time"] == None: self.event["submit_time"] = 'NULL'
            if self.event["prepare_time"] == None: self.event["prepare_time"] = 'NULL'

    def get_id(self):
        return self.event["governance_object_id"]

    def set_prepared(self):
        self.event["prepare_time"] = calendar.timegm(time.gmtime())

    def set_submitted(self):
        self.event["submit_time"] = calendar.timegm(time.gmtime())

    def save(self):
        sql = """
            INSERT INTO event 
                (governance_object_id, start_time, prepare_time, submit_time)
            VALUES
                (%(governance_object_id)s,%(start_time)s,%(prepare_time)s,%(submit_time)s)
            ON DUPLICATE KEY UPDATE
                governance_object_id=%(governance_object_id)s,
                start_time=%(start_time)s,
                prepare_time=%(prepare_time)s,
                submit_time=%(submit_time)s
        """

        mysql.db.query(sql % self.event)