import os
import json
import sqlite3

import logging
logging.basicConfig(level=logging.WARNING)

import pandas as pd
from dotenv import load_dotenv

load_dotenv('secrets.env')

BOTEX_DB = 'data/exp_runs/honesty_botex_db_2024-05-23.sqlite3'
OTREE_DATA = 'data/exp_runs/honesty_otree_2024-05-23.csv'

conn = sqlite3.connect(BOTEX_DB)
cursor = conn.cursor()
cursor.execute("SELECT * FROM conversations")
conversations = cursor.fetchall()
cursor.execute("SELECT * FROM participants")
sessions = cursor.fetchall()
cursor.close()
conn.close()

otree_raw = pd.read_csv(OTREE_DATA, index_col= False)




def extract_participant_data(otree_raw, exp):
    wide = otree_raw.loc[
        (otree_raw['participant._current_app_name'] == exp) 
        # Adjust this above to the last page of the experiment
    ].reset_index()
    if wide.shape[0] == 0: return None
    long = pd.melt(
        wide, id_vars='participant.code', ignore_index=False
    ).reset_index()
        
    vars = [
        'participant.time_started_utc', 'participant.payoff', 'session.code',
        f'{exp}.1.player.id_in_group',
        f'{exp}.10.player.comprehension_check1', f'{exp}.10.player.comprehension_check2',
        f'{exp}.10.player.human_check', f'{exp}.10.player.feedback'
    ]

    participants = long.loc[
        long['variable'].isin(vars)
    ].pivot_table(
        index = 'participant.code', columns = 'variable', values = 'value',
        aggfunc = 'first'
    ).reset_index().rename(columns = {
        'participant.code': 'participant_code',
        'session.code': 'session_code',
        f'{exp}.1.player.id_in_group': 'player_id',
        'participant.time_started_utc': 'time_started',
        f'{exp}.10.player.comprehension_check1': 'comprehension_check1',
        f'{exp}.10.player.comprehension_check2': 'comprehension_check2',
        f'{exp}.10.player.manipulation_check': 'manipulation_check',
        f'{exp}.10.player.human_check': 'human_check',
        f'{exp}.10.player.feedback': 'feedback'
    })
    participants['experiment'] = exp
    participants['player_id'] = participants['player_id'].astype(int)
    participants['comprehension_check1'] = pd.to_numeric(participants['comprehension_check1'], errors='coerce').astype('Int64')
    participants['comprehension_check2'] = pd.to_numeric(participants['comprehension_check2'], errors='coerce').astype('Int64')
    participants['human_check'] = pd.to_numeric(participants['human_check'], errors='coerce').astype('Int64')

    ordered_columns = [
        'experiment', 'session_code', 'participant_code', 'time_started', 
        'player_id',  
        'comprehension_check1', 'comprehension_check2',
        'human_check', 'feedback'
    ]

    return participants[ordered_columns]

def extract_round_data(otree_raw, exp):
    wide = otree_raw.loc[
        (otree_raw['participant._current_app_name'] == exp) 
        # Adjust this above to the last page of the experiment
    ].reset_index()
    if wide.shape[0] == 0: return None
    long = pd.melt(
        wide, id_vars=['session.code', f'{exp}.1.player.id_in_group'], 
        ignore_index=False
    ).reset_index().rename(columns = {
        'session.code': 'session_code',
        f'{exp}.1.player.id_in_group': 'player_id'
    })
        
    vars = [
        [f'{exp}.{r}.player.true_amount', f'{exp}.{r}.player.reported_amount']
        for r in range(1, 11)
    ]  
    vars = [item for sublist in vars for item in sublist]

    rounds = long.loc[
        long['variable'].isin(vars)
    ].copy()
    rounds['player_id'] = rounds['player_id'].astype(int)
    rounds['round'] = rounds['variable'].str.extract(r'(\d+)').astype(int)
    rounds['var'] = rounds['variable'].str.extract(rf'{exp}\.\d+\.player\.(\w+)')
    rounds['experiment'] = exp
    rounds = rounds.pivot_table(
        index = ['experiment', 'session_code', 'player_id', 'round'], 
        columns = 'var', values = 'value', aggfunc = 'first'
    ).sort_index().reset_index()
    rounds['true_amount'] = pd.to_numeric(rounds['true_amount'], errors='coerce').astype('Int64')
    rounds['reported_amount'] = pd.to_numeric(rounds['reported_amount'], errors='coerce').astype('Int64')
    return rounds 

def extract_rationales(participant_code):
    reason = []        
    c = pd.DataFrame(conversations)
    if not any(c[0] == participant_code):
        logging.warning(f"participant {participant_code} not found in conversations")
        return None           
    conv = json.loads(c.loc[c[0] == participant_code, 2].item())
    check_for_error = False
    for message in conv:
        if message['role'] == 'assistant':
                try:
                    resp_str = message['content']
                    start = resp_str.find('{', 0)
                    end = resp_str.rfind('}', start)
                    resp_str = resp_str[start:end+1]
                    cont = json.loads(resp_str)
                    if 'questions' in cont:
                        for q in cont['questions']: 
                            if q['id'] == "id_reported_amount": 
                                reason.append(q['reason'])
                                check_for_error = True
                except:
                    logging.info(
                        f"message :'{message['content']}' failed to load as json"
                    )
                    continue
        else:
            if message['content'][:7] != 'Perfect' and check_for_error:
                reason.pop()
            check_for_error = False
    if len(reason) != 10: 
        logging.warning(f"""
            Error parsing bot conversation for participant {participant_code} 
            (delivers reasons for {len(reason)} responses)
        """)
        return None

    return reason

participants = pd.concat([
    extract_participant_data(otree_raw, 'honesty'),
    extract_participant_data(otree_raw, 'fhonesty')
])
rounds = pd.concat([
    extract_round_data(otree_raw, 'honesty'),
    extract_round_data(otree_raw, 'fhonesty')
])

rounds['reported_amount_reason'] = ""
for s in participants.session_code.unique():
    ps = participants.loc[
        participants.session_code == s, 'participant_code'
    ].tolist()
    for p in ps:
        p_id = participants.loc[
            participants.participant_code == p, 'player_id'
        ].item()
        rounds.loc[
            (rounds.session_code == s) & (rounds.player_id == p_id),
            'reported_amount_reason'
        ] = extract_rationales(p)
     
participants.to_csv('data/generated/honesty_participants.csv', index = False)
rounds.to_csv('data/generated/honesty_rounds.csv', index = False)