#!/bin/env python3
import numpy as np

np.random.seed(835845000375724 % (2**32))

with open("attendees.txt") as f:
    attendees = sorted(l.strip() for l in f.readlines() if not l.startswith('#'))

with open("speakers.txt") as f:
    speakers = [l.strip() for l in f.readlines() if not l.startswith('#')]
# print(speakers)

week = len(speakers) + 1
assert all(pers in attendees for pers in speakers)

with open("zeros.txt") as f:
    zeros = [l.strip().split(', ') for l in f.readlines() if not l.startswith('#')]

assert len(zeros) == week - 1

weights = np.array(
    [(not speakers[-1] == pers) / (1 + speakers.count(pers)) for pers in attendees]
)


weights /= sum(weights)

# print(random.choices(attendees, weights=weights, k=3))
print(np.random.choice(attendees, size=3, replace=False, p=weights))
