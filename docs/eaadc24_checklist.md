# To Do for EAA Classroom Experiment

Prior to the session:
- [X]: Make sure that the OpenAI account has enough funds.
- [X]: Set CELL_SIZE in `code/run_eaadc_session.py` to 18
- [X]: Restart docker oTree container on Server. Verify that it starts up OK holds no data
- [X]: Backup and delete existing botex_db.sqlite3 file on laptop
- [X]: Make sure that SESSION_ID is empty in `code/run_eaadc_session.py`
- [X]: Run `code/run_eaadc_session.py` with LL_RUNS_ONLY = True
- [X]: Insert session_id in `code/run_eaadc_session.py` (SESSION_ID)
- [X]: Create fallback slide deck on LL dyads only
- [ ]: Make sure that the Internet connection is working reliably in the session room.

During the session: 
- [ ]: Run `code/run_eaadc_session.py`
- [ ]: Monitor the progress of the experiment

When experiment is complete:
- [ ]: Download the results from oTree Server
- [ ]: Run `code/extact_mftust_exp_data.py`
- [ ]: Render `docs/eaadc24_talk.quarto`
