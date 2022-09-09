#!/bin/env python3
import sys, io
import numpy as np
import re
from datetime import datetime as dt

BETA = np.log(2)
EMAIL = "quantumcroupier@gmail.com"
MEDALS = ["🥇", "🥈", "🥉"]
RNGBOT_ID = 1128726096546025472  # twitter used id
RNGBOT_URL = "https://twitter.com/rndgenbot"


terminal = print
_print = print

if sys.argv[1:] and sys.argv[1] == '--dry':
    DRY = True
    sys.argv.pop(1)
else:
    DRY = False

if sys.argv[2:]:
    passwd = sys.argv[2]
    email = True
    mail = io.StringIO()

    def print(*args, **kwargs):
        terminal(*args, **kwargs)
        _print( *args, **kwargs, file=mail)

    croupier = lambda *args, **kwargs: terminal(*args, **kwargs, file=mail)
else:
    email = False
    croupier = lambda *args, **kwargs: None

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
if llz: print("weight doubled for zeroing 2 weeks ago: " + ", ".join(llz))
if lz:  print("weight doubled for zeroing last week:   " + ", ".join(lz))
if z:   print("zeroed this week: " + ", ".join(z))
assert len(set(z + lz + llz)) == len(z + lz + llz), "someone zeroed out too often!!"
print()

if sys.argv[1:]:
    import tweepy

    TW_TOKEN = sys.argv[1]
    twitter = True
    client = tweepy.Client(bearer_token=TW_TOKEN)
    tweets = client.get_users_tweets(RNGBOT_ID).data[:3]
    print("@rndgenbot's latest tweets are: [1], [2], [3]")
    seed_base = ""
    for tw in tweets:
        (a, b) = map(int, *re.findall("numbers are (\d{,2}) and (\d{,3})!", tw.text))
        seed_base += f'{a:02}{b:03}'

    print()
    print(f"base seed is b={seed_base}")
    seed_base = int(seed_base)
else:
    seed_base = int(input("enter (base) seed: "))


# seed = 835845000375724 % (2**32)
seed = seed_base % (2**32)

np.random.seed(seed)

print(f"seed = b % 2^32 = {seed}")
print()

# compute probabilites & draw --------------------------------------------------

count = np.fromiter(map(speakers.count, attendees), dtype=int)
weights = (
    np.exp(-BETA * count)
    * (attendees != speakers[-1])  # speaker gets weight 0
    * 2 ** np.isin(attendees, lz)  # x2 weight for ppl who zeroed in the past 2 weeks
    * 2 ** np.isin(attendees, llz)
    * (1 - np.isin(attendees, z))  # zero out
)
weights /= sum(weights)

pad = max(14, *(len(p) for p in attendees))
croupier('<pre style="font-size: 13px">', end='')
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
croupier('</pre>', end='')

winners = np.random.choice(attendees, size=3, replace=False, p=weights)
print(f"\nAnd the winner is ... ", end="")
croupier('<marquee><b>', end='')
print(f"🎉 {winners[0]} 🎉", end='')
croupier('</marquee></b>', end='')
print()
croupier(
    "If you can't talk tomorrow for some reason please reply-all ASAP so that the backup speaker may prepare"
)

print()
print("The backups are:")
for n, pers in enumerate(winners[1:]):
    print(f"{n + 2}. {pers}{MEDALS[n+1]}")

if twitter:
    print()
    for i, tw in enumerate(tweets):
        terminal(f'{[i+1]} https://twitter.com/rndgenbot/status/{tw.id}')

croupier('Alea iacta est,\nthe 🎲<a href="https://github.com/zstier/qtfm">Quantum Croupier</a>🎲')

# send email -------------------------------------------------------------------
SUBJECT = "The 🎲Quantum Croupier🎲 is pleased to announce tomorrow's speaker."

if not email:
    exit()
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

with open("emails.txt") as f:
    to_addrs = [l.strip() for l in f.readlines()]
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
for i, tw in enumerate(tweets):
    text = text.replace(f'[{i+1}]', f'<a href="https://twitter.com/rndgenbot/status/{tw.id}">[{i+1}]</a>')

message = MIMEMultipart()
message["From"] = "quantumcroupier@math.berkeley.edu"
message["To"] = ",".join(to_addrs)
message["Reply-to"] = ",".join(to_addrs)
message["Subject"] = SUBJECT
message.attach(MIMEText(text.encode("utf8"), "html", _charset="utf8"))

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as conn:
    conn.login(EMAIL, passwd)
    conn.sendmail(from_addr=EMAIL, to_addrs=to_addrs, msg=message.as_string())
