import os
import json
import sqlite3

import logging
logging.basicConfig(level=logging.WARNING)

import pandas as pd
from dotenv import load_dotenv

load_dotenv('secrets.env')

BOTEX_DB = 'data/exp_runs/deception_botex_db_2024-03-24.sqlite3'
OTREE_DATA = [
    f'data/exp_runs/deception_otree_{i}_2024-03-24.csv' for i in range(1, 4)
]

conn = sqlite3.connect(BOTEX_DB)
cursor = conn.cursor()
cursor.execute("SELECT * FROM conversations")
conversations = cursor.fetchall()
cursor.execute("SELECT * FROM sessions")
sessions = cursor.fetchall()
cursor.close()
conn.close()

def extract_participant_data(otree_raw, exp):
    wide = otree_raw.loc[
        (otree_raw['participant._current_app_name'] == exp) &
        (otree_raw['participant._index_in_pages'] == 6) 
        # Adjust this above to the last page of the experiment
    ].reset_index()
    if wide.shape[0] == 0: return None
    long = pd.melt(
        wide, id_vars='participant.code', ignore_index=False
    ).reset_index()
        
    vars = [
        'participant.time_started_utc', 'participant.payoff', 'session.code',
        f'{exp}.1.group.id_in_subsession', f'{exp}.1.player.id_in_group',
        f'{exp}.1.player.comprehension_check1', f'{exp}.1.player.comprehension_check2',
        f'{exp}.1.player.human_check', f'{exp}.1.player.feedback', 
    ]

    participants = long.loc[
        long['variable'].isin(vars)
    ].pivot_table(
        index = 'participant.code', columns = 'variable', values = 'value',
        aggfunc = 'first'
    ).reset_index().rename(columns = {
        'participant.code': 'participant_code',
        'session.code': 'session_code',
        'participant.payoff': 'payoff',
        'participant.time_started_utc': 'time_started',
        f'{exp}.1.group.id_in_subsession': 'group_id',
        f'{exp}.1.player.id_in_group': 'role_in_group',
        f'{exp}.1.player.comprehension_check1': 'comprehension_check1',
        f'{exp}.1.player.comprehension_check2': 'comprehension_check2',
        f'{exp}.1.player.human_check': 'human_check',
        f'{exp}.1.player.feedback': 'feedback'
    })
    participants['experiment'] = exp
    participants['group_id'] = participants['group_id'].astype(int)
    participants['role_in_group'] = participants['role_in_group'].astype(int)
    participants['payoff'] = participants['payoff'].astype(int)
    participants['comprehension_check1'] = participants['comprehension_check1'].astype(int)
    participants['comprehension_check2'] = participants['comprehension_check2'].astype(int)
    participants['human_check'] = participants['human_check'].astype(int)   

    ordered_columns = [
        'experiment', 'session_code', 'participant_code', 'time_started', 
        'group_id', 'role_in_group', 'payoff', 
        'comprehension_check1', 'comprehension_check2', 'human_check', 'feedback'
    ]

    return participants[ordered_columns]

def extract_round_data(otree_raw, exp):
    wide = otree_raw.loc[
        (otree_raw['participant._current_app_name'] == exp) &
        (otree_raw['participant._index_in_pages'] == 6) 
        # Adjust this above to the last page of the experiment
    ].reset_index()
    if wide.shape[0] == 0: return None
    long = pd.melt(
        wide, id_vars=['session.code', f'{exp}.1.group.id_in_subsession'], 
        ignore_index=False
    ).reset_index().rename(columns = {
        'session.code': 'session_code',
        f'{exp}.1.group.id_in_subsession': 'group_id'
    })
        
    vars = [
        [f'{exp}.{r}.group.message', f'{exp}.{r}.group.choice']
        for r in range(1, 2)
    ]  
    vars = [item for sublist in vars for item in sublist]

    rounds = long.loc[
        long['variable'].isin(vars)
    ].copy()
    rounds['group_id'] = rounds['group_id'].astype(int)
    rounds['round'] = rounds['variable'].str.extract(r'(\d+)').astype(int)
    rounds['var'] = rounds['variable'].str.extract(rf'{exp}\.\d+\.group\.(\w+)')
    rounds['experiment'] = exp
    rounds = rounds.pivot_table(
        index = ['experiment', 'session_code', 'group_id', 'round'], 
        columns = 'var', values = 'value', aggfunc = 'first'
    ).sort_index().reset_index()
    rounds['message'] = rounds['message'].astype(int)
    rounds['choice'] = rounds['choice'].astype(int)
    return rounds 

def extract_rationales(participant_code):
    reason = []        
    c = pd.DataFrame(conversations)        
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
                            if q['id'] == "id_message" or q['id'] == "id_choice": 
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
    if len(reason) != 1: 
        logging.warning(f"""
            Error parsing bot conversation for participant {participant_code} 
            (delivers reasons for {len(reason)} responses)
        """)
        return None

    return reason


for otree_file_no, otree_file in enumerate(OTREE_DATA):
    otree_raw = pd.read_csv(otree_file, index_col= False)

    participants = pd.concat([
        extract_participant_data(otree_raw, 'deception'),
        extract_participant_data(otree_raw, 'fdeception')
    ])
    rounds = pd.concat([
        extract_round_data(otree_raw, 'deception'),
        extract_round_data(otree_raw, 'fdeception')
    ])

    rounds['message_reason'] = ""
    rounds['choice_reason'] = ""
    for s in participants.session_code.unique():
        ps = participants.loc[
            participants.session_code == s, 'participant_code'
        ].tolist()
        for p in ps:
            g = participants.loc[
                participants.participant_code == p, 'group_id'
            ].item()
            r = participants.loc[
                participants.participant_code == p, 'role_in_group'
            ].item()
            if int(r) == 1:
                rounds.loc[
                    (rounds.session_code == s) & (rounds.group_id == g),
                    ['message_reason']
                ] = extract_rationales(p)
            else:
                rounds.loc[
                    (rounds.session_code == s) & (rounds.group_id == g),
                    'choice_reason'
                ] = extract_rationales(p)
     
    participants.to_csv(f'data/generated/deception_{otree_file_no+1}_participants.csv', index = False)
    rounds.to_csv(f'data/generated/deception_{otree_file_no+1}_rounds.csv', index = False)


mparticipants = pd.concat([
    pd.read_csv(f'data/generated/deception_{i}_participants.csv') 
    for i in range(1, 4)
]).drop_duplicates().sort_values(
    by = ['experiment', 'session_code', 'group_id', 'role_in_group']
)
mrounds = pd.concat([
    pd.read_csv(f'data/generated/deception_{i}_rounds.csv') 
    for i in range(1, 4)
]).drop_duplicates().sort_values(
    by = ['experiment', 'session_code', 'group_id']
)
for i in range(1, 4):
    os.remove(f'data/generated/deception_{i}_participants.csv')
    os.remove(f'data/generated/deception_{i}_rounds.csv')

mparticipants.to_csv('data/generated/deception_participants.csv', index = False)
mrounds.to_csv('data/generated/deception_rounds.csv', index = False)
