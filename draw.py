#!/bin/env python3
import numpy as np

# import random

np.random.seed(835845000375724 % (2**32))

speakers = []
attendees = []
weights = []

with open("speakers.txt") as file:
    speakers = [l.strip() for l in file.readlines()]
# print(speakers)

with open("attendees.txt") as file:
    attendees = sorted(map(str.strip, file.readlines())

weights = np.array([(not speakers[-1] == pers) / (1 + speakers.count(pers)) for pers in attendees])

weights /= sum(weights)

# print(random.choices(attendees, weights=weights, k=3))
print(np.random.choice(attendees, size=3, replace=False, p=weights))

"""
import numpy as np
vec=[1,2,3]
P=[0.5,0.2,0.3]
np.random.choice(vec,size=2,replace=False, p=P)
"""

"""
tot = 0
for s in attendees.keys():
	tot += attendees[s]
for s in attendees.keys():
	attendees[s] /= tot

val = random()
tally = 0
for s in attendees.keys():
	tally += attendees[s]
	if tally > val:
		print("speaker is", s)
		break
"""
