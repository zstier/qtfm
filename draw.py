#!/bin/env python3
import numpy as np

BETA = np.log(2)

np.random.seed(835845000375724 % (2**32))

with open("attendees.txt") as f:
    attendees = np.array([l.strip() for l in f.readlines() if not l.startswith("#")])
attendees.sort()

with open("speakers.txt") as f:
    speakers = [l.strip() for l in f.readlines() if not l.startswith("#")]
# print(speakers)
week = len(speakers) + 1

print(f"Week {week}")

with open("zeros.txt") as f:
    zeros = [l.strip().split(", ") for l in f.readlines() if not l.startswith("#")]
    for z in zeros:
        if "" in z:
            z.remove("")
    # Now let's do a bunch of sanity checks!
    assert (
        len(zeros) >= week
    ), "zeros.txt needs to have at least (# past talks) + 1 lines"
    assert not any(zeros[week:]), "people have zeroed out for future weeks??"


for pers in set(speakers):
    if pers not in attendees:
        print(f"WARN: speaker {pers} is not attendee")
for pers in set(p for wk in zeros for p in wk):
    if pers not in attendees:
        print(f'WARN: zeroed-out person "{pers}" is not attendee')

llz, lz, z = [[], [], *zeros][-3:]
print("weight doubled for zeroing 2 weeks ago: " + ", ".join(llz))
print("weight doubled for zeroing last week:   " + ", ".join(lz))
print("zeroed this week: " + ", ".join(z))
assert len(set(z + lz + llz)) == len(z + lz + llz), "someone zeroed out too often!!"
print()

count = np.fromiter(map(speakers.count, attendees), dtype=int)
weights = (
    np.exp(-BETA * count)
    * (attendees != speakers[-1])
    * (1 + np.isin(attendees, lz))
    * (1 + np.isin(attendees, llz))
    * (1 - np.isin(attendees, z))
)
weights /= sum(weights)

pad = max(7, *(len(p) for p in attendees))
print("Speaker", " " * (pad - 7), "prob")
print("-" * (2 + pad + 5))
for pers, prob in zip(attendees, weights):
    print(pers, " " * (pad - len(pers)), f"{prob:.3}")

# print(random.choices(attendees, weights=weights, k=3))
print("\nAnd the winners are...")
print(np.random.choice(attendees, size=3, replace=False, p=weights))
