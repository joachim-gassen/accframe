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
