#!/bin/env python3
import sys, io
import numpy as np
import re
from datetime import datetime as dt
from functools import reduce
from operator import or_

BETA = np.log(2)
EMAIL = "quantumcroupier@gmail.com"
MEDALS = ["🥇", "🥈", "🥉"]
RNGBOT_ID = 1128726096546025472  # twitter used id
RNGBOT_URL = "https://twitter.com/rndgenbot"
BEACON_URL = 'https://api.drand.sh'


def twitter_rand(tw_token):
    import tweepy
    # tw_token = sys.argv[1]
    twitter = True
    client = tweepy.Client(bearer_token=tw_token)
    global tweets
    tweets = client.get_users_tweets(RNGBOT_ID).data[:3]
    print("@rndgenbot's latest tweets are: [1], [2], [3]")
    seed_base = ""
    for tw in tweets:
        (a, b) = map(int, *re.findall(r"numbers are (\d{,2}) and (\d{,3})!", tw.text))
        seed_base += f"{a:02}{b:03}"

    print()
    print(f"base seed is b={seed_base}")
    return int(seed_base)


def beacon_rand():
    import urllib.request as req
    from io import BytesIO
    import json
    import time
    # now = int(time.strftime('%s'))
    # info = json.load(req.urlopen(f'{BEACON_URL}/info'))
    # delta = now - info['genesis_time']
    # round = int(delta / int(info['period']) + .99)
    data = json.load(req.urlopen(f'{BEACON_URL}/public/latest'))
    print(f'drand beacon round {data["round"]}')
    print(f'randomness is {data["randomness"]}')
    return int(data['randomness'], 16)
    


import argparse
parser = argparse.ArgumentParser(prog='Quantum Croupier')
parser.add_argument('-t', '--twitter', action='store',
                    help='twitter API key (not working anymore)')
parser.add_argument('-b', '--beacon', action='store_true',
                    help='toggle for using drand randomness beacon')
parser.add_argument('-e', '--email', action='store',
                    help='login token for email')
parser.add_argument('--dry', action='store_true',
                    help='perform a dry run')
args = parser.parse_args()

if args.twitter and args.beacon:
    print('twitter and beacon sources are incompatible')


terminal = _print = print

DRY = args.dry

if args.email:
    passwd = args.email
    email = True
    mail = io.StringIO()

    def print(*a, **kwargs):
        terminal(*a, **kwargs)
        _print(*a, **kwargs, file=mail)

    croupier = lambda *a, **kwargs: terminal(*a, **kwargs, file=mail)
else:
    email = False
    croupier = lambda *a, **kwargs: None

def debug(*a, **kwargs):
    terminal(*a, **kwargs)
    if DRY and args.email:
        _print(*a, **kwargs, file=mail)

# read and validate input -----------------------------------------------------

with open("attendees.txt") as f:
    attendees = np.array([l.strip() for l in f.readlines() if not l.startswith("#")])
attendees.sort()

with open("speakers.txt") as f:
    speakers = [l.strip() for l in f.readlines() if not l.startswith("#")]
# print(speakers)
week = len(speakers) + 1

if DRY: print("=" * 10 + "DRY RUN" + "=" * 10)
print("=" * 10 + f" Week {week} " + "=" * 10)
print(f"It is {dt.now().strftime('%Y-%m-%d %H:%M:%S')}.")

with open("miss.txt") as f:
    misses = [{x for x in l.strip().split(",") if x} for l in f.readlines()]
assert len(misses) >= week, "miss.txt missing line for this week"
misses = misses[:week]
missing = misses[week - 1]

with open("zeros.txt") as f:
    zeros = [{x for x in l.strip().split(",") if x} for l in f.readlines()]
assert len(zeros) >= week, "zeros.txt missing line for this week"
assert not any(zeros[week:]), "people have zeroed out for future weeks??"
zeros = zeros[:week]
z = zeros[week-1]

for pers in set(speakers) - set(attendees):
    debug(f'WARN: speaker "{pers}" is not attendee')
for pers in reduce(or_, zeros, set()) - set(attendees):
    debug(f'WARN: zeroed-out person "{pers}" is not attendee')
for pers in reduce(or_, misses,set()) - set(attendees):
    debug(f'WARN: missing person "{pers}" is not attendee')

# remove non-attendees from list of zeros and misses
zeros = [z & set(attendees) for z in zeros]
misses = [z & set(attendees) for z in misses]
missing &= set(attendees)

llz, lz = set(), set()
for zj, mj, last_spk in zip(zeros[:-1], misses, speakers):
    assert not zj & mj, "People missing don't need to zero out: " + ", ".join(zj & mj)
    assert not (intr := zj & (lz | llz)), "zeroing while boosted:" + ", ".join(intr)

    # llz = (llz & mj) | (lz - mj) 
    # missing the week after you speak shouldn't be detrimental
    llz = (llz & mj) | (lz - mj) - {last_spk}
    lz = (lz & mj) | zj # lz for next week!

lz - missing and print("weight doubled for zeroing (first time): " + ", ".join(lz - missing))
llz - missing and print("weight doubled for zeroing (second time): " + ", ".join(llz - missing))
z and print("zeroed this week: " + ", ".join(z))
missing and print("missing this week: " + ", ".join(missing))
print()

# if sys.argv[1:]:
#     ...
# else:
#     seed_base = int(input("enter (base) seed: "))
#     twitter = False

# seed = 835845000375724 % (2**32)

if args.beacon:
    seed_base = beacon_rand()
elif args.twitter:
    seed_base = twitter_rand(args.twitter)
else:
     seed_base = int(input("enter (base) seed: "))
     twitter = False
seed = seed_base % 2**32

np.random.seed(seed)

print(f"seed = b % 2^32 = {seed}")
print()

# compute probabilites & draw --------------------------------------------------

count = np.fromiter(map(speakers.count, attendees), dtype=int)

weights = (
    np.exp(-BETA * count)
    * (attendees != speakers[-1])  # last speaker gets weight 0
    * 2 ** np.isin(attendees, list(lz)) # boost (1st time)
    * 2 ** np.isin(attendees, list(llz)) # boost (2nd time)
    * (1 - np.isin(attendees, list(z)))  # zero out
    * (1 - np.isin(attendees, list(missing)))  # missing
)
weights /= sum(weights)

pad = max(14, *(len(p) for p in attendees))
croupier('<pre style="font-size: 13px">', end="")
print("🎲 Participant", " " * (pad - 11), "prob  🎲")
print("-" * (5 + pad + 8))
for i, (pers, prob) in enumerate(zip(attendees, weights)):
    print(
        ["⬛", "🟥"][i % 2],
        pers,
        " " * (pad - len(pers)),
        f"{prob:.3f}",
        ["⬛", "🟥"][(i + 1) % 2],
    )
croupier("</pre>", end="")

winners = np.random.choice(attendees, size=3, replace=False, p=weights)
print(f"\nAnd the winner is ... ", end="")
croupier("<marquee><b>", end="")
print(f"🎉 {winners[0]} 🎉", end="")
croupier("</marquee></b>", end="")
print()
croupier(
    "If you can't talk tomorrow for some reason please "
    "reply-all ASAP so that the backup speaker may prepare"
)

print()
print("The backups are:")
for n, pers in enumerate(winners[1:]):
    print(f"{n + 2}. {pers}{MEDALS[n+1]}")

if args.twitter:
    print()
    for i, tw in enumerate(tweets):
        terminal(f"{[i+1]} https://twitter.com/rndgenbot/status/{tw.id}")

croupier(
    'Alea iacta est,\nthe 🎲<a href="https://github.com/zstier/qtfm">Quantum Croupier</a>🎲'
)

# send email -------------------------------------------------------------------
SUBJECT = (
    "[DRY] " * DRY + "The 🎲Quantum Croupier🎲 is pleased to announce tomorrow's speaker."
)

if not email:
    exit()

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

with open("emails.txt") as f:
    to_addrs = [l.strip() for l in f.readlines() if not l.startswith("#")]
    if DRY:
        to_addrs = to_addrs[:1]

text = (
    '<font style="font-size: 13px" face="DejaVu Sans Mono, Courier, Courier New, monospace">'
    + mail.getvalue()
    .replace("\n", "<br>")
    .replace("@rndgenbot", f'<a href="{RNGBOT_URL}">@rndgenbot</a>')
    + "</font>"
)
# text = re.sub(r"(🎉.*🎉)", "<marquee><b>\\1</b></marquee>", text)
if args.twitter:
    for i, tw in enumerate(tweets):
        text = text.replace(
            f"[{i+1}]",
            f'<a href="https://twitter.com/rndgenbot/status/{tw.id}">[{i+1}]</a>',
        )

if args.beacon:
    text = re.sub(
        'beacon round (\d+)',
        rf'beacon <a href="{BEACON_URL}/public/\1">round \1</a>',
        text
    )

message = MIMEMultipart()
message["From"] = "quantumcroupier@math.berkeley.edu"
message["To"] = ",".join(to_addrs)
message["Reply-to"] = ",".join(to_addrs)
message["Subject"] = SUBJECT
message.attach(MIMEText(text.encode("utf8"), "html", _charset="utf8"))

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as conn:
    conn.login(EMAIL, passwd)
    conn.sendmail(from_addr=EMAIL, to_addrs=to_addrs, msg=message.as_string())
