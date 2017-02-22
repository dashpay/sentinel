import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../lib')))
import init
import misc
from models import Transient
from misc import printdbg
import time
import random


class Scheduler(object):
    transient_key_scheduled = 'NEXT_SENTINEL_CHECK_AT'
    random_interval_max = 720

    @classmethod
    def is_run_time(self):
        next_run_time = Transient.get(self.transient_key_scheduled) or 0
        now = misc.now()

        printdbg("current_time = %d" % now)
        printdbg("next_run_time = %d" % next_run_time)

        return now >= next_run_time

    @classmethod
    def clear_schedule(self):
        Transient.delete(self.transient_key_scheduled)

    @classmethod
    def schedule_next_run(self, random_interval=None):
        if not random_interval:
            random_interval = self.random_interval_max

        next_run_at = misc.now() + random.randint(1, random_interval_max)
        printdbg("scheduling next sentinel run for %d" % next_run_at)
        Transient.set(self.transient_key_scheduled, next_run_at,
                      next_run_at)
