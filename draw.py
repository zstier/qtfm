import numpy as np
# import random

np.random.seed(835845000375724%(2**32))

speakers = []
attendees = []
weights = []

with open("speakers.txt") as file:
	lines = file.readlines()
for x in lines:
	s = x
	if x[-1] == '\n':
		s = x[:-1]
	speakers.append(s)
# print(speakers)

with open("attendees.txt") as file:
	lines = file.readlines()
for x in lines:
	s = x
	if x[-1]=='\n':
		s = x[:-1]
	# print(s)
	attendees.append(s)
	weights.append(0)
	for t in speakers:
		if t == s:
			weights[-1] += 1
# print(attendees)
for s in range(len(attendees)):
	if attendees[s] == speakers[-1]:
		weights[s] = 0
	else:
		weights[s] = 1/(1+weights[s])
# print(attendees,weights)

tot = 0
for s in range(len(attendees)):
	tot += weights[s]
for s in range(len(attendees)):
	weights[s] /= tot

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
