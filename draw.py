#!/bin/env python3
import sys, io
import numpy as np
BETA = np.log(2)
EMAIL = 'quantumcroupier@gmail.com'
MEDALS = ['🥇', '🥈', '🥉']

if sys.argv[1:]:
    passwd = sys.argv[1]
    email = True
    _print = print
    mail = io.StringIO()
    def print(*args):
        _print(*args)
        _print(*args, file=mail)
else:
    email = False


seed = 835845000375724 % (2**32)

np.random.seed(seed)

# read and validate input -----------------------------------------------------

with open("attendees.txt") as f:
    attendees = np.array([l.strip() for l in f.readlines() if not l.startswith("#")])
attendees.sort()

with open("speakers.txt") as f:
    speakers = [l.strip() for l in f.readlines() if not l.startswith("#")]
# print(speakers)
week = len(speakers) + 1

print("=" * 10 + f" Week {week} " + "=" * 10)

print()
print(f'seed = {seed}')
print()

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
llz and print("weight doubled for zeroing 2 weeks ago: " + ", ".join(llz))
lz and print("weight doubled for zeroing last week:   " + ", ".join(lz))
z and print("zeroed this week: " + ", ".join(z))
assert len(set(z + lz + llz)) == len(z + lz + llz), "someone zeroed out too often!!"
print()


# comute probabilites & draw ---------------------------------------------------

count = np.fromiter(map(speakers.count, attendees), dtype=int)
weights = (
    np.exp(-BETA * count)
    * (attendees != speakers[-1])
    * (1 + np.isin(attendees, lz))
    * (1 + np.isin(attendees, llz))
    * (1 - np.isin(attendees, z))
)
weights /= sum(weights)

pad = max(11, *(len(p) for p in attendees))
print("Participant", " " * (pad - 11), "prob")
print("-" * (2 + pad + 5))
for pers, prob in zip(attendees, weights):
    print(pers, " " * (pad - len(pers)), f"{prob:.3}")

winners = np.random.choice(attendees, size=3, replace=False, p=weights)
print(f"\nAnd the winner is... {winners[0]}🎉")


print("The backups are:")
for n, pers in enumerate(winners[1:]):
    print(f"{n + 1}. {pers}{MEDALS[n+1]}")


# send email

if not email: exit()
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

with open('emails.txt') as f:
    to_addrs = [l.strip() for l in f.readlines()]

text = '<font face="Courier, Courier New, monospace">' + mail.getvalue().replace('\n','<br>').replace(' ', '&nbsp;') + '</font>'

message = MIMEMultipart()
message['From'] = EMAIL
message['To'] = 'recipient-superposition'
message['Subject'] = 'The 🎲Quantum Croupier🎲 is pleased to announce tomorrows speaker.'
message.attach(MIMEText(text.encode('utf8'), 'html', _charset='utf8'))

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as conn:
     conn.login(EMAIL, passwd)
     conn.sendmail(from_addr=EMAIL, to_addrs=to_addrs, msg=message.as_string())
