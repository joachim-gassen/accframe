import subprocess
import time
import os
import dotenv
import shutil
import datetime

import logging
logging.basicConfig(level=logging.INFO)

import botex

OTREE_IS_RUNNING = False
OTREE_STARTUP_WAIT = 3
PART_SESSION = 10
PART_BY_COND = 100 # Needs to be a multiple of PART_SESSION

dotenv.load_dotenv("secrets.env")

if not OTREE_IS_RUNNING:
    log = open('data/generated/otree_log_giftex.txt','w') 
    os.environ["OTREE_PRODUCTION"] = "1"
    otree_proc = subprocess.Popen(
        ["otree", "devserver"], cwd="otree",
        stderr=log, stdout=log
    )
    time.sleep(OTREE_STARTUP_WAIT)

for i in range(PART_BY_COND//PART_SESSION):
    sdict = botex.init_otree_session(config_name = "giftex", npart = PART_SESSION)
    botex.run_bots_on_session(session_id = sdict['session_id'])
    time.sleep(5)

    sdict = botex.init_otree_session(config_name = "fgiftex", npart = PART_SESSION)
    botex.run_bots_on_session(session_id = sdict['session_id'])
    time.sleep(5)

botex_data_fname = f"giftex_botex_db_{datetime.date.today().isoformat()}.sqlite3"
logging.info(f"Storing botex data as '{botex_data_fname}'.")
shutil.copy(os.environ.get('BOTEX_DB'), f"data/exp_runs/{botex_data_fname}")
logging.info(f"Done! Export data from oTree before stopping the server.")
