# Preregistered Experiments

2024-05-24 17:18 CEDT

- Pushed final code changes to accframe repo and tagged a release v0.1.0
- Ran `make dbclean` to remove all data from the botex and oTree databases
- OpenAI Cost balance prior to running the experiments: $48.67
- 17:23 starting honesty experiment by sourcing `code/run_honesty_exp.py`
- 17:36 P7 (jkm951by) of session (hhtoysou) got delayed on 32/50. Seemed like an OpenAI timeout. Paused and resumed the thread and then it continued.
- 17:40 session 'hhtoysou' finished. 
- 17:51 P1 (8ylkvcer) and P6 (qs6gh3k8) got delayed in session (70mg7uk5). After ~10 minutes they continued without any intervention.
- 17:57 session '70mg7uk5' finished.
- 18:11 Again, three clients were delayed and continued without intervention app. ~10 minutes later.
- 18:14 session '7z1z1z1z' finished.
- 18:29 the pattern continues (two bots delayed) in session 'ejtuaj1m'
- 18:30 session 'ejtuaj1m' finished.
- 18:48 session '22ornojh' finished.
- 18:52 Charged 100 USD to OPenAI API account and set up auto recharge.
- 18:59 session '9u2vr33o' finished
- 19:00 stopped close monitoring
- 19:15 Running session 'hppg9a7r' all good
- 19:35 Running session '5nkgmx88' all good
- 19:50 Running session '5ss1kyth' all good
- 20:19 Running session '89ogs35n' all good
- 20:22 session '89ogs35n' finished
- 20:33 Running session 'x0znrxkn' all good
- 20:36 session 'x0znrxkn' finished
- 20:45 session '7cfc0h6x' finished
- 20:47 Error message Exception has occurred: KeyError
'summary'
  File "/Users/joachim/github/botex/src/botex/bot.py", line 339, in run_bot
    if not full_conv_history: summary = resp['summary']
                                        ~~~~^^^^^^^^^^^
KeyError: 'summary'
The summary was included as a key in the question response dict. Fixed it by manually adding the summary to the response dict.
- 21:12 It seems as if the thread has bailed out anyhow. Participant code: 'e4ou3fwe', session: '1bnqypl7'
- 21:16 Running session 's9is1luv' all good
- 21:22 session 's9is1luv' finished
- 21:46 code run_honesty_exp.py finished (did finish earlier)
- 21:47 Exported oTree data for honesty experiment

2024-05-25 07:09 CEDT

- 07:09 Parsing data with code/extract_honesty_exp_data.py worked but generated warning that participant `e4ou3fwe` was not found in the botex database. Also, for participant '22w71lht' only 11 answer reasons were found in the conversation data (needs checking)
- 07:34 OpenAI Costs for 2024-05-24 accframe: USD 51.98, current total cost: USD 92.03
- 07:59 The participant that dropped out was P77. There is no point in rerunning it in the session as the conversation data from the partial run is lost. Alternatively, we could rerun a session with just this participant. 
- 09:14 The participant with incomplete reasoning data is conv[136] and the problematic message is idx 08. It is supposed to contain only a summary but it also includes a question_id key because of the botex code only requiring the relevant keys to be present but not checking for additional keys. Applied manual fix in import code.
- 09:35 Tightened the botex code to be stricter when parsing bot responses (commit 606a578)
- 09:28 OpenAI Costs for 2024-05-24 accframe: USD 81.93, current total cost: USD 92.03
- 09:42 pushed honesty data to the repo
- 09:43 Ran `make cleandb` to remove otree and botex databases
- 09:43 Running trust experiment by sourcing `code/run_trust_exp.py`
- 09:51 session 'enh4eivm' finished
- 09:55 stopped close monitoring 
- 10:25 sesssion 'o14bejoi' running (one dyad delayed)
- 10:31 session 'o14bejoi' finished
- 10:33 oTree stopped responding. 
- 10:35 timeout exception in botex when scanning web page because otree is not responing. Aborted experiment
- 10:42 Copied botex data to `data/exp_runs/trust_botex_db_2024-05-25_otree_crashed.sqlite3`. oTree data is empty.
- 10:44 Ran `make cleandb` to remove otree and botex databases
- 10:45 OpenAI Costs for 2024-05-25 accframe: USD 18.08
- 10:46 Restarting trust experiment by sourcing `code/run_trust_exp.py`
- 11:02 Session 'sayi5knu' started. All good.
- 11:48 timeout exception in botex when scanning web page. oTree is not responding (again...)
- 11:50 Copied botex data to `data/exp_runs/trust_botex_db_2024-05-25_otree_crashed_2.sqlite3`. oTree data is empty.
- 11:55 Ran `make cleandb` to remove otree and botex databases
- 11:56 OpenAI Costs for 2024-05-25 accframe: USD 44.84
- 12:02 Staring oTree server in production mode on console with `export OTREE_PRODUCTION=1 && otree prodserver` to check for error messages during the next run
- 12:02 Restarting trust experiment by sourcing `code/run_trust_exp.py`
- 12:42 Session '7d2c24f4' started. All good.
- 13:00 oTree wait page deadlock in session '7d2c24f4'
- 13:42 Changed wait parsing in botex to timeouting and retrying after 10 seconds.
- 13:42 Stored interim version of oTree and botex databases
- 13:42 OpenAI Costs for 2024-05-25 accframe: USD 67.53
- 13:43 Restarted trust experiment by sourcing `code/run_trust_exp.py` for 70 participants
- 13:53 Session 'meqa97y3' started. All good.
- 14:01 Session 'iy8m858d' started. All good.
- 15:44 Trust experiment complete. Exported oTree data.
- 16:02 Parsing data with code/extract_trust_exp_data.py (code needed some minor adjustments to deal with missing data)
- 16:07 OpenAI Costs for 2024-05-25 accframe: USD 121.09
- 16:14 Ran `make cleandb` to remove otree and botex databases
- 16:15 Running gift exchange experiment by sourcing `code/run_giftex_exp.py` (otree in production mode)
- 16:18 Haha! After a few minutes oTree become unresponsive. I think I know why. It writes to stdoout/sterr and the buffer is full. I will redirect the output to a file. Starting the process again after running `make cleandb`
- 16:07 OpenAI Costs for 2024-05-25 accframe: USD 121.74
- 16:20 Running gift exchange experiment by sourcing `code/run_giftex_exp.py` (otree in development mode and with logfile)
- 17:51 Running session 'voreu3wn'. All good. Stopped close monitoring.
- 18:20 Running session 'o8wvrcul'. All good.
- 19:32 Running session 'uqd3koma'. All good.
- 19:55 Running session 'x568zqb7'. All good.
- 20:28 Running session '36ur7ggy'. All good.
- 20:51 Running session 'l8knzj3u'. All good.
- 21:06 Running session 'h17nvk1b'. All good.
- 21:18 Running session 'h17nvk1b'. All good.
- 21:22 Gift Exchange experiment complete. Exported oTree data.
- 21:25 Parsing data with code/extract_giftex_exp_data.py
