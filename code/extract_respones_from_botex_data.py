import logging
logging.basicConfig(level=logging.INFO)

from botex import export_response_data


BOTEX_DB = 'data/exp_runs/honesty_botex_db_2024-06-17.sqlite3'
export_response_data('data/generated/honesty_2024-06-17_responses.csv', BOTEX_DB)
BOTEX_DB = 'data/exp_runs/giftex_botex_db_2024-06-18.sqlite3'
export_response_data('data/generated/giftex_2024-06-18_responses.csv', BOTEX_DB)
BOTEX_DB = 'data/exp_runs/trust_botex_db_2024-06-18.sqlite3'
export_response_data('data/generated/trust_2024-06-18.responses.csv', BOTEX_DB)
