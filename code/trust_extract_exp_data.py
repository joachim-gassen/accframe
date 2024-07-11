import sys
import json
import sqlite3

import logging
logging.basicConfig(level=logging.WARNING)

import pandas as pd
from dotenv import load_dotenv

load_dotenv('secrets.env')

if len(sys.argv) == 2:
    DATA_VERSION = sys.argv[1]
else: DATA_VERSION = '2024-06-18'

BOTEX_DB = f'data/exp_runs/trust_botex_db_{DATA_VERSION}.sqlite3'
OTREE_DATA = f'data/exp_runs/trust_otree_{DATA_VERSION}.csv'

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
    ].reset_index()
    if wide.shape[0] == 0: return None
    long = pd.melt(
        wide, id_vars='participant.code', ignore_index=False
    ).reset_index()
        
    vars = [
        'participant.time_started_utc', 'participant.payoff', 'session.code',
        f'{exp}.1.group.id_in_subsession', f'{exp}.1.player.id_in_group',
        f'{exp}.10.player.comprehension_check', f'{exp}.10.player.manipulation_check',
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
        'participant.payoff': 'payoff',
        'participant.time_started_utc': 'time_started',
        f'{exp}.1.group.id_in_subsession': 'group_id',
        f'{exp}.1.player.id_in_group': 'role_in_group',
        f'{exp}.10.player.comprehension_check': 'comprehension_check',
        f'{exp}.10.player.manipulation_check': 'manipulation_check',
        f'{exp}.10.player.human_check': 'human_check',
        f'{exp}.10.player.feedback': 'feedback'
    })
    participants['experiment'] = exp
    participants['group_id'] = participants['group_id'].astype(int)
    participants['role_in_group'] = participants['role_in_group'].astype(int)
    participants['payoff'] = participants['payoff'].astype(int)
    participants['comprehension_check'] = pd.to_numeric(participants['comprehension_check'], errors='coerce').astype('Int64')
    participants['manipulation_check'] = pd.to_numeric(participants['manipulation_check'], errors='coerce').astype('Int64')
    participants['human_check'] = pd.to_numeric(participants['human_check'], errors='coerce').astype('Int64')  

    ordered_columns = [
        'experiment', 'session_code', 'participant_code', 'time_started', 
        'group_id', 'role_in_group', 'payoff', 
        'comprehension_check', 'manipulation_check',
        'human_check', 'feedback'
    ]

    return participants[ordered_columns]

def extract_round_data(otree_raw, exp):
    wide = otree_raw.loc[
        (otree_raw['participant._current_app_name'] == exp) 
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
        [f'{exp}.{r}.group.sent_amount', f'{exp}.{r}.group.sent_back_amount']
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
    rounds['sent_amount'] = rounds['sent_amount'].astype(int)
    rounds['sent_back_amount'] = rounds['sent_back_amount'].astype(int)
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
                    cont = json.loads(resp_str, strict=False)
                    if 'questions' in cont:
                        for q in cont['questions']: 
                            if q['id'] == "id_sent_amount" or q['id'] == "id_sent_back_amount": 
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
    extract_participant_data(otree_raw, 'trust'),
    extract_participant_data(otree_raw, 'ftrust')
])
rounds = pd.concat([
    extract_round_data(otree_raw, 'trust'),
    extract_round_data(otree_raw, 'ftrust')
])

rounds['sent_reason'] = ""
rounds['sent_back_reason'] = ""
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
                ['sent_reason']
            ] = extract_rationales(p)
        else:
            rounds.loc[
                (rounds.session_code == s) & (rounds.group_id == g),
                'sent_back_reason'
            ] = extract_rationales(p)
     
participants.to_csv(f'data/generated/trust_{DATA_VERSION}_participants.csv', index = False)
rounds.to_csv(f'data/generated/trust_{DATA_VERSION}_rounds.csv', index = False)