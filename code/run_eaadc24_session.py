import dotenv
dotenv.load_dotenv("secrets.env")

import botex

SESSION_ID = '2e78n6pa'

# Needs to be an even number.
# For the EAA session, CELL_SIZE = 18 -> 54 humans and 54 bots
CELL_SIZE = 18
LL_RUNS_ONLY = False

is_human = [False, False]*CELL_SIZE + [False, True]*(CELL_SIZE//2) + \
    [True, False]*(CELL_SIZE//2) + [True, True]*CELL_SIZE

if SESSION_ID == '':
    sdict = botex.init_otree_session(
        config_name = "mftrust", npart = CELL_SIZE*6,
        is_human = is_human, room_name = "eaadc24"
    )
    print(f"EAA Session initialized with {6*CELL_SIZE} participants. Session ID: {sdict['session_id']}")
    session_id = sdict['session_id']
else:
    session_id = SESSION_ID

if LL_RUNS_ONLY:
    print(f"Running bot on bot dyads of EAA session {session_id}")
    bot_urls = botex.get_bot_urls(session_id = session_id)
    botex.run_bots_on_session(session_id = session_id, bot_urls=bot_urls[slice(2*CELL_SIZE)])
else:
    print(f"Running bots on all (remaining) dyads of EAA session {session_id}")    
    botex.run_bots_on_session(session_id = session_id, already_started=False)


print(f"Done! Export data from oTree before stopping the server.")
