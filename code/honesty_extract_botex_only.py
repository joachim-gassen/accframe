# We used this code to extract data from an experiment run where oTree terminated
# after the experiment was completed. We used the botex data to recconstruct the
# data from the experiment. 

import sys
import csv
import logging
logging.basicConfig(level=logging.WARNING)

from botex import read_participants_from_botex_db, read_responses_from_botex_db

from dotenv import load_dotenv
load_dotenv('secrets.env')

if len(sys.argv) == 2:
    DATA_VERSION = sys.argv[1]
else: DATA_VERSION = '2024-10-19'

f = open('data/generated/honesty_true_amounts.csv')
reader = list(csv.DictReader(f))
ta = [row for row in reader]
f.close()

BOTEX_DB = f'data/exp_runs/honesty_botex_db_{DATA_VERSION}.sqlite3'

bpdata = read_participants_from_botex_db(botex_db = BOTEX_DB)
brdata = read_responses_from_botex_db(botex_db = BOTEX_DB)

def get_peq_data(session_code, participant_code):
    peq_data = dict()
    for pd in brdata:
        if pd['session_id'] == session_code and pd['participant_id'] == participant_code:
            if pd['question_id'] == 'id_comprehension_check1':
                peq_data['comprehension_check1'] = 1 if pd['answer'] == "Only I" else 2
            elif pd['question_id'] == 'id_comprehension_check2':
                peq_data['comprehension_check2'] = 2 if \
                pd['answer'] == "Reporting the actual amount in each round" or \
                pd['answer'] == "Filing a budget request for the actual costs in each round" \
                else 1
            elif pd['question_id'] == 'id_human_check':
                peq_data['human_check'] = 2 if pd['answer'] == "I am a Bot" else 1
            elif pd['question_id'] == 'id_feedback':
                peq_data['feedback'] = pd['answer']
        if all(k in peq_data for k in ['comprehension_check1', 'comprehension_check2', 'human_check', 'feedback']):
            break
    return peq_data

def get_round_data(session_code, participant_code, round):
    for rd in brdata:
        if rd['session_id'] == session_code and \
            rd['participant_id'] == participant_code and \
            rd['round'] == round:
            if rd['question_id'] == 'id_reported_amount':
                return {'response': int(rd['answer'][:4]), 'reason': rd['reason']}
    return {'response': None, 'reason': None}

pdata_list = []
rdata_list = []
for i, bdict in enumerate(bpdata):
    pdata = dict()
    pdata['experiment'] = bdict['session_name']
    pdata['session_code'] = bdict['session_id']
    pdata['participant_code'] = bdict['participant_id']
    pdata['time_started'] = bdict['time_in']
    pdata['player_id'] = (i + 1) % 10 if (i + 1) % 10 > 0 else 10
    peq_data = get_peq_data(pdata['session_code'], pdata['participant_code'])
    pdata['comprehension_check1'] = peq_data['comprehension_check1']
    pdata['comprehension_check2'] = peq_data['comprehension_check2']
    pdata['human_check'] = peq_data['human_check']
    pdata['feedback'] = peq_data['feedback']
    pdata_list.append(pdata)
    for j in range(10):
        rdata = dict()
        rdata['experiment'] = pdata['experiment']
        rdata['session_code'] = pdata['session_code']
        rdata['player_id'] = pdata['player_id']
        rdata['round'] = j + 1
        rdata['true_amount'] = ta[(i // 20) * 100 + (i % 10) * 10 + j]['true_amount']
        rdata_response = get_round_data(
            pdata['session_code'], pdata['participant_code'], rdata['round']
        )
        rdata['reported_amount'] = rdata_response['response']
        rdata['reported_amount_reason'] = rdata_response['reason']
        rdata_list.append(rdata)

def write_ldict_to_csv(ldict, filename):
    with open(filename  , 'w') as f:
        writer = csv.DictWriter(f, fieldnames=ldict[0].keys())
        writer.writeheader()
        for row in ldict:
            writer.writerow(row)


     
write_ldict_to_csv(pdata_list, f'data/generated/honesty_{DATA_VERSION}_participants.csv')
write_ldict_to_csv(rdata_list, f'data/generated/honesty_{DATA_VERSION}_rounds.csv')
