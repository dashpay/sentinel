#!/usr/bin/env python

import dashd
import json
import cPickle

def process():
    pass

    """
        - employees and employers get paid each month depending on their first initial of their last name (A = 1st, D=4th, Z=26th)

        For each payment, it happens deterministically:
            - Block #1 - salary
            - Block #2-12 - expenses (sorted by submission date)

        Example:
            - 4th : Evan Duffield (#2 payment, plane ticket, #3 payment, exhibit booth, etc)
            - 4th : Daniel Diaz
            - 23rd : Robert W

        Payments are governance objects, which must be voted on by network. Sentineel consensus powers the system.
    """