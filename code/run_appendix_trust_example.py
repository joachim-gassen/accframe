import subprocess
import time
import os
import dotenv

import botex

# When running this do not forget to set the game to one round
# in otree/trust/__init__.py
# and to delete data/exp_runs/app_example.sqlite3
# before running this script

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
