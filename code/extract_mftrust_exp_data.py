import os
import json
import sqlite3

import logging
logging.basicConfig(level=logging.WARNING)

import pandas as pd
from dotenv import load_dotenv

load_dotenv('secrets.env')

BOTEX_DB = 'data/exp_runs/eaatrial_botex_db_2024-05-09.sqlite3'
OTREE_DATA = 'data/exp_runs/eaatrial_otree_2024-05-09.csv'

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
    long = pd.melt(
        otree_raw, id_vars='participant.code', ignore_index=False
    ).reset_index()
        
    vars = [
        'participant.time_started_utc', 'participant.payoff', 'session.code',
        'participant.part_id',
        f'{exp}.1.group.id_in_subsession', f'{exp}.1.player.id_in_group',
        f'{exp}.1.group.message',
        f'{exp}.3.player.comprehension_check', f'{exp}.3.player.manipulation_check',
        f'{exp}.3.player.human_check', f'{exp}.3.player.feedback'
    ]

    participants = long.loc[
        long['variable'].isin(vars)
    ].pivot_table(
        index = 'participant.code', columns = 'variable', values = 'value',
        aggfunc = 'first'
    ).reset_index().rename(columns = {
        'participant.code': 'participant_code',
        'session.code': 'session_code',
        'participant.part_id': 'participant_id',
        'participant.payoff': 'payoff',
        'participant.time_started_utc': 'time_started',
        f'{exp}.1.group.id_in_subsession': 'group_id',
        f'{exp}.1.player.id_in_group': 'role_in_group',
        f'{exp}.1.group.message': 'group_message',
        f'{exp}.3.player.comprehension_check': 'comprehension_check',
        f'{exp}.3.player.manipulation_check': 'manipulation_check',
        f'{exp}.3.player.human_check': 'human_check',
        f'{exp}.3.player.feedback': 'feedback'
    })
    participants['experiment'] = exp
    participants['group_id'] = participants['group_id'].astype(int)
    participants['role_in_group'] = participants['role_in_group'].astype(int)
    participants['payoff'] = pd.to_numeric(participants['payoff'], errors='coerce').astype('Int64')
    participants['comprehension_check'] = pd.to_numeric(participants['comprehension_check'], errors='coerce').astype('Int64')
    participants['manipulation_check'] = pd.to_numeric(participants['manipulation_check'], errors='coerce').astype('Int64')
    participants['human_check'] = pd.to_numeric(participants['human_check'], errors='coerce').astype('Int64')

    ordered_columns = [
        'experiment', 'session_code', 'participant_code', 'participant_id',
        'time_started', 
        'group_id', 'role_in_group', 'group_message', 'payoff', 
        'comprehension_check', 'manipulation_check',
        'human_check', 'feedback'
    ]

    return participants[ordered_columns].set_index(['session_code','group_id','role_in_group']).sort_index().reset_index()

def extract_round_data(otree_raw, exp):
    wide = otree_raw.loc[
        (otree_raw['participant._current_app_name'] == exp) 
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
        [f'{exp}.{r}.group.sent_amount', f'{exp}.{r}.group.sent_back_amount']
        for r in range(1, 4)
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
    rounds['sent_amount'] = pd.to_numeric(rounds['sent_amount'], errors='coerce').astype('Int64')
    rounds['sent_back_amount'] = pd.to_numeric(rounds['sent_back_amount'], errors='coerce').astype('Int64')
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
    if len(reason) != 3: 
        logging.warning(f"""
            Error parsing bot conversation for participant {participant_code} 
            (delivers reasons for {len(reason)} responses)
        """)
        return None

    return reason

participants = pd.concat([extract_participant_data(otree_raw, 'mftrust')])

rounds = pd.concat([extract_round_data(otree_raw, 'mftrust')])

rounds['sent_reason'] = ""
rounds['sent_back_reason'] = ""
s = participants.session_code.unique()
participants['is_human'] = [p[3] for p in sessions if p[1] in s]
ps = [p[2] for p in sessions if p[3] == 0 and p[1] in s]
for p in ps:
    g = participants.loc[
        participants.participant_code == p, 'group_id'
    ].item()
    r = participants.loc[
        participants.participant_code == p, 'role_in_group'
    ].item()
    if int(r) == 1:
        rounds.loc[
        (rounds.group_id == g), ['sent_reason']
        ] = extract_rationales(p)
    else:
        rounds.loc[
            (rounds.group_id == g), ['sent_back_reason']
        ] = extract_rationales(p)
     
participants.to_csv('data/generated/eaatrial2_participants.csv', index = False)
rounds.to_csv('data/generated/eaatrial2_rounds.csv', index = False)