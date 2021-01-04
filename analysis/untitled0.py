# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 22:16:16 2021

@author: cb6
"""

FILE = 'wurwolves-revert-xvilf6esqygyc-logs-1609798033272.log'


lines = open(FILE, 'r').readlines()

import re
import numpy as np

states = [l for l in lines if "heroku[router]: at=info method=GET path=\"/api/boy-if-name-break/state?" in l]

times =[
        int(re.search(r"service=(\d+)ms", s).groups(1)[0])
        for s in states
        ]

# %%

import matplotlib.pyplot as plt
import version_info as vs


plt.figure()
plt.plot(times)


plt.figure()
plt.hist(times)
plt.title("Time taken to serve a state")
plt.xlabel("Time / ms")
vs.tag_plot(small=True)