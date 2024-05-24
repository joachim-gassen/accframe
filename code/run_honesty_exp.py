import subprocess
import time
import os
import shutil
import dotenv
import csv

import logging
logging.basicConfig(level=logging.INFO)

import botex

OTREE_IS_RUNNING = False
OTREE_STARTUP_WAIT = 3
ROUNDS = 10
PART_SESSION = 10

dotenv.load_dotenv("secrets.env")

f = open('data/generated/honesty_true_amounts.csv')
reader = list(csv.DictReader(f))
ta = [row for row in reader]
f.close()

if not OTREE_IS_RUNNING:
    os.environ["OTREE_PRODUCTION"] = "1"
    otree_proc = subprocess.Popen(
        ["otree", "devserver"], cwd="otree",
        stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    time.sleep(OTREE_STARTUP_WAIT)

for r in range(1):
    session_ta = ta[r*ROUNDS*PART_SESSION:(r+1)*ROUNDS*PART_SESSION]
    for i in range(PART_SESSION):
        for j in range(i*ROUNDS, (i+1)*ROUNDS):
            session_ta[j]['id_in_group'] = i + 1
    with open('otree/honesty/true_amounts.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames = session_ta[0].keys())
        writer.writeheader()
        writer.writerows(session_ta)
    shutil.copy('otree/honesty/true_amounts.csv', 'otree/fhonesty/')

    sdict = botex.init_otree_session(
        config_name = "honesty", npart = PART_SESSION
    )
    botex.run_bots_on_session(session_id = sdict['session_id'])
    time.sleep(5)

    sdict = botex.init_otree_session(config_name = "fhonesty", npart = 10)
    botex.run_bots_on_session(session_id = sdict['session_id'])
    time.sleep(5)

logging.info(f"Done! Export data from oTree before stopping the server.")
