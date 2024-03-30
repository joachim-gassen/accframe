import subprocess
import time
import os
import dotenv

import logging
logging.basicConfig(level=logging.INFO)

import botex

OTREE_IS_RUNNING = True
OTREE_STARTUP_WAIT = 3

dotenv.load_dotenv("secrets.env")

if not OTREE_IS_RUNNING:
    os.environ["OTREE_PRODUCTION"] = "1"
    otree_proc = subprocess.Popen(
        ["otree", "devserver"], cwd="otree",
        stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    time.sleep(OTREE_STARTUP_WAIT)

for i in range(1):
#    sdict = botex.init_otree_session(config_name = "gift", npart = 10)
#    botex.run_bots_on_session(session_id = sdict['session_id'])
#    time.sleep(5)

    sdict = botex.init_otree_session(config_name = "fgift", npart = 2)
    botex.run_bots_on_session(session_id = sdict['session_id'])
    time.sleep(5)

logging.info(f"Done! Export data from oTree before stopping the server.")
