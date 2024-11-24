import os
import time
import subprocess
import dotenv

import logging
logging.basicConfig(level=logging.INFO)

import botex

OTREE_IS_RUNNING = False
OTREE_STARTUP_WAIT = 3

# Make sure that NUM_ROUNDS is set to 1 in otree/trust/__init__.py
# prior to running this script

dotenv.load_dotenv("secrets.env")

BOTEX_DB = "data/exp_runs/trust_appendix_example.sqlite3"

if os.path.exists(BOTEX_DB):
    logging.info("Trust example data already exists. Renaming the file.")
    os.rename(BOTEX_DB, BOTEX_DB + ".bak")
  
if not OTREE_IS_RUNNING:
    log = open('data/generated/otree_log_trust.txt','w') 
    os.environ["OTREE_PRODUCTION"] = "1"
    otree_proc = subprocess.Popen(
        ["otree", "devserver"], cwd="otree",
        stderr=log, stdout=log
    )
    time.sleep(OTREE_STARTUP_WAIT)

trust = botex.init_otree_session(
  config_name = "trust", npart = 2,   
  botex_db = BOTEX_DB
)

botex.run_bots_on_session(
  session_id = trust['session_id'],
  botex_db = BOTEX_DB
)