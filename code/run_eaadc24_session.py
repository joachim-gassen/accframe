import dotenv
dotenv.load_dotenv("secrets.env")

import botex

# For the EAA session, CELL_SIZE = 18 -> 54 humans and 54 bots
CELL_SIZE = 4

is_human = [False, False]*CELL_SIZE + [False, True]*(CELL_SIZE//2) + \
    [True, False]*(CELL_SIZE//2) + [True, True]*CELL_SIZE

sdict = botex.init_otree_session(
    config_name = "mftrust", npart = CELL_SIZE*6,
    is_human = is_human, room_name = "eaadc24"
)
print(f"EAA Session started with {6*CELL_SIZE} participants. Session ID: {sdict['session_id']}")

botex.run_bots_on_session(session_id = sdict['session_id'])

print(f"Done! Export data from oTree before stopping the server.")
