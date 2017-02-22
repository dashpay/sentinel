
import json
import os
import time
import random

from misc import printdbg

class Scheduler:

    def __init__(self):
        printdbg("Scheduler.loadSchedule: __init__")
        # Test code, not sure how the path should be determined
        self.schedulePath = "sentinel-schedule.json"
        self.loadSchedule()

    def runThisTime(self):
        printdbg("Scheduler.runThisTime: Start, schedule = %s" % (self.schedule))
        now = int(time.time())
        hour = now // 3600
        if hour != self.schedule['hour']:
            self.createSchedule()
        nexttime = None
        if len(self.schedule['offsets']) > 0:
            offset = self.schedule['offsets'][0]
            stime = 3600 * hour + offset
            printdbg("Scheduler.runThisTime: offset = %s, stime = %s" % (offset, stime))
            if now >= stime:
                nexttime = stime
        printdbg("Scheduler.runThisTime: nexttime = %s" % (nexttime))
        if nexttime is not None:
            self.schedule['offsets'].pop(0)
            self.storeSchedule()
            return True
        return False

    def loadSchedule(self):
        printdbg("Scheduler.loadSchedule: Start")
        self.schedule = None
        if os.path.exists(self.schedulePath):
            try:
                self.schedule = json.loads(file(self.schedulePath).read())
            except:
                print("Scheduler.loadSchedule: WARNING: Load exception")
        if (self.schedule is None) or (not self.checkScheduleFormat()):
            self.createSchedule()
        now = int(time.time())
        hour = now // 3600
        if self.schedule['hour'] > hour:
            self.createSchedule()

    def createSchedule(self):
        printdbg("Scheduler.createSchedule: Start")
        now = int(time.time())
        hour = now // 3600
        currentOffset = now % 3600
        nrunsperhour = 6.0
        nruns = int(nrunsperhour * (3600. - float(currentOffset)) / 3600.)
        printdbg("Scheduler.createSchedule: currentOffset = %s, nrunsperhour = %s, nruns = %s" % (currentOffset, nrunsperhour, nruns))
        offsets = [random.randint(currentOffset+1, 3599) for i in range(nruns)]
        offsets.sort()
        self.schedule = {'hour': hour,
                         'offsets': offsets}
        self.storeSchedule()
        printdbg("Scheduler.createSchedule: schedule = %s" % (str(self.schedule)))
        
    def storeSchedule(self):
        printdbg("Scheduler.storeSchedule: Start")
        jsonSchedule = json.dumps(self.schedule)
        ofile = file(self.schedulePath, "w")
        ofile.write(jsonSchedule)
        
    def checkScheduleFormat(self):
        printdbg("Scheduler.checkScheduleFormat: Start")
        if not isinstance(self.schedule, dict):
            return False
        if 'hour' not in self.schedule:
            return False
        if 'offsets' not in self.schedule:
            return False
        if not isinstance(self.schedule['offsets'], list):
            return False
        printdbg("Scheduler.checkScheduleFormat: returning True")
        return True
