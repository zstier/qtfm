#!/bin/env python3
import numpy as np

BETA = np.log(2)

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

count = np.fromiter(map(speakers.count, attendees), dtype=int)
weights = np.exp(-BETA * count) * (np.array(attendees) != speakers[-1])
weights /= sum(weights)

pad = max(7, *(len(p) for p in attendees))
print('Speaker', ' ' * (pad - 7), 'prob')
print('-' * (2 + pad + 5))
for pers, prob in zip(attendees, weights):
    print(pers, ' ' * (pad - len(pers)), f'{prob:.3}')

# print(random.choices(attendees, weights=weights, k=3))
print('\nAnd the winners are...')
print(np.random.choice(attendees, size=3, replace=False, p=weights))
