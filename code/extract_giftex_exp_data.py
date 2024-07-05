import os
import json
import sqlite3

import logging
logging.basicConfig(level=logging.WARNING)

import pandas as pd
from dotenv import load_dotenv

load_dotenv('secrets.env')

#DATA_VERSION = '2024-05-25'
DATA_VERSION = '2024-06-18'
#DATA_VERSION = '2024-07-02'

BOTEX_DB = f'data/exp_runs/giftex_botex_db_{DATA_VERSION}.sqlite3'
OTREE_DATA = f'data/exp_runs/giftex_otree_{DATA_VERSION}.csv'

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
        (otree_raw['participant._current_app_name'] == exp) &
        (otree_raw['participant._index_in_pages'] == 100) 
        # Adjust this above to the last page of the experiment
    ].reset_index()
    if wide.shape[0] == 0: return None
    long = pd.melt(
        wide, id_vars='participant.code', ignore_index=False
    ).reset_index()
        
    vars = [
        'participant.time_started_utc', 'participant.payoff', 'session.code',
        f'{exp}.1.group.id_in_subsession', f'{exp}.1.player.id_in_group',
        f'{exp}.1.player.comprehension_check_pre1', f'{exp}.1.player.comprehension_check_pre2',
        f'{exp}.10.player.comprehension_check_post1', f'{exp}.10.player.comprehension_check_post2',
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
        f'{exp}.1.group.id_in_subsession': 'group_id',
        f'{exp}.1.player.id_in_group': 'player_id',
        'participant.time_started_utc': 'time_started',
        f'{exp}.1.player.comprehension_check_pre1': 'comprehension_check_pre1',
        f'{exp}.1.player.comprehension_check_pre2': 'comprehension_check_pre2',
        f'{exp}.10.player.comprehension_check_post1': 'comprehension_check_post1',
        f'{exp}.10.player.comprehension_check_post2': 'comprehension_check_post2',
        f'{exp}.10.player.human_check': 'human_check',
        f'{exp}.10.player.feedback': 'feedback'
    })
    participants['experiment'] = exp
    participants['group_id'] = participants['group_id'].astype(int)
    participants['player_id'] = participants['player_id'].astype(int)
    participants['comprehension_check_pre1'] = participants['comprehension_check_pre1'].astype(int)
    participants['comprehension_check_pre2'] = participants['comprehension_check_pre2'].astype(int)
    participants['comprehension_check_post1'] = participants['comprehension_check_post1'].astype(int)
    participants['comprehension_check_post2'] = participants['comprehension_check_post2'].astype(int)
    participants['human_check'] = participants['human_check'].astype(int)   

    ordered_columns = [
        'experiment', 'session_code', 'participant_code', 'time_started', 
        'group_id', 'player_id',  
        'comprehension_check_pre1', 'comprehension_check_pre2',
        'comprehension_check_post1', 'comprehension_check_post2',
        'human_check', 'feedback'
    ]

    return participants[ordered_columns]

def extract_round_data(otree_raw, exp):
    wide = otree_raw.loc[
        (otree_raw['participant._current_app_name'] == exp) &
        (otree_raw['participant._index_in_pages'] == 100) 
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
        [f'{exp}.{r}.group.wage', f'{exp}.{r}.group.effort']
        for r in range(1, 11)
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
    rounds['wage'] = rounds['wage'].astype(int)
    rounds['effort'] = rounds['effort'].astype(float)
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
                            if q['id'] == "id_wage" or q['id'] == "id_effort": 
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
    extract_participant_data(otree_raw, 'giftex'),
    extract_participant_data(otree_raw, 'fgiftex')
])
rounds = pd.concat([
    extract_round_data(otree_raw, 'giftex'),
    extract_round_data(otree_raw, 'fgiftex')
])

rounds['wage_reason'] = ""
rounds['effort_reason'] = ""
for s in participants.session_code.unique():
    ps = participants.loc[
        participants.session_code == s, 'participant_code'
    ].tolist()
    for p in ps:
        g = participants.loc[
            participants.participant_code == p, 'group_id'
        ].item()
        r = participants.loc[
            participants.participant_code == p, 'player_id'
        ].item()
        if int(r) == 1:
            rounds.loc[
                (rounds.session_code == s) & (rounds.group_id == g),
                ['wage_reason']
            ] = extract_rationales(p)
        else:
            rounds.loc[
                (rounds.session_code == s) & (rounds.group_id == g),
                'effort_reason'
            ] = extract_rationales(p)
     
participants.to_csv(f'data/generated/giftex_{DATA_VERSION}_participants.csv', index = False)
rounds.to_csv(f'data/generated/giftex_{DATA_VERSION}_rounds.csv', index = False)
