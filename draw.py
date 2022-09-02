#!/bin/env python3
import numpy as np

np.random.seed(835845000375724 % (2**32))

with open("speakers.txt") as file:
    speakers = [l.strip() for l in file.readlines()]
# print(speakers)

with open("attendees.txt") as file:
    attendees = sorted(map(str.strip, file.readlines()))

weights = np.array(
    [(not speakers[-1] == pers) / (1 + speakers.count(pers)) for pers in attendees]
)

weights /= sum(weights)

# print(random.choices(attendees, weights=weights, k=3))
print(np.random.choice(attendees, size=3, replace=False, p=weights))
