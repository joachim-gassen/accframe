import sqlite3
import csv
import botex

OTREE_FILE = 'data/exp_runs/giftex_otree_2024-10-22.csv'
SQLITE_INPUT = 'data/exp_runs/giftex_botex_db_2024-10-22_long.sqlite3'
SQLITE_OUTPUT = 'data/exp_runs/giftex_botex_db_2024-10-22.sqlite3'

session_ids = set()
with open(OTREE_FILE, mode='r') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        session_ids.add(row['session.code'])
session_ids = list(session_ids)

conn_in = sqlite3.connect(SQLITE_INPUT)
cursor_in = conn_in.cursor()

place_holder = ','.join(['?' for _ in session_ids])
query = f"SELECT * FROM participants WHERE session_id IN ({place_holder})"
cursor_in.execute(query, session_ids)
filtered_participants = cursor_in.fetchall()

participant_ids = [p[2] for p in filtered_participants]
place_holder = ','.join(['?' for _ in participant_ids])
query = f"SELECT * FROM conversations WHERE id IN ({place_holder})"
cursor_in.execute(query, participant_ids)
filtered_conversations = cursor_in.fetchall()
conn_in.close()

botex.setup_botex_db(SQLITE_OUTPUT)

conn_out = sqlite3.connect(SQLITE_OUTPUT)
cursor_out = conn_out.cursor()
place_holders = ','.join(['?' for _ in filtered_participants[0]])
cursor_out.executemany(f"INSERT INTO participants VALUES ({place_holders})", filtered_participants)
place_holders = ','.join(['?' for _ in filtered_conversations[0]])
cursor_out.executemany(f"INSERT INTO conversations VALUES ({place_holders})", filtered_conversations)
conn_out.commit()
conn_out.close()
