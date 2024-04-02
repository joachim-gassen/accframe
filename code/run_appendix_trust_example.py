import subprocess
import time
import os
import dotenv

import botex

BOTEX_DB = 'data/exp_runs/app_example.sqlite3'
OTREE_IS_RUNNING = False
OTREE_STARTUP_WAIT = 3

dotenv.load_dotenv("secrets.env")

if not OTREE_IS_RUNNING:
    os.environ["OTREE_PRODUCTION"] = "1"
    otree_proc = subprocess.Popen(
        ["otree", "devserver"], cwd="otree",
        stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    time.sleep(OTREE_STARTUP_WAIT)

import botex

trust = botex.init_otree_session(
  config_name = "trust", npart = 2, 
  botex_db = BOTEX_DB
)

botex.run_bots_on_session(
  session_id = trust['session_id'],
  botex_db = BOTEX_DB
)
