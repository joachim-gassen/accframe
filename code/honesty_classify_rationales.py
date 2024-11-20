from os import environ
import json
import logging
logging.basicConfig(level=logging.INFO)

import pandas as pd
from litellm import completion

import dotenv
dotenv.load_dotenv("secrets.env")

system_prompt = """
    I need you to classify a set of statements that participants made during an 
    online experiment when rationalizing their decisions during the experiment.
    You have to classify the statements along the following categories:
    1. How much does it reveal that the person cares about maximizing their own payoff?
    2. How much does it reveal that the person cares about the other experimental participant's payoff?
    3. How much does it reveal that the person cares about reporting the truth?
    For each category, you need to return a score between 1 and 10, where 1 means
    that the statement does not reveal the category at all, and 10 means that the
    statement reveals the category completely.
    Please return the scores in the following format JSON format:
    {
        "self_payoff": 5,
        "other_payoff": 3,
        "truth": 7
    }
"""


def classify_response(statement, model = "gpt-4o", openai_api_key = None):
    if openai_api_key is None: openai_api_key = environ.get('OPENAI_API_KEY')
    conversation = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]
    conversation.append({
        "role": "user",
        "content": f"Here comes the statement that I want you to classify: {statement}"
    })
    logging.info(f"Classifying the statement: {statement}")
    attempts = 0
    max_attempts = 5
    resp_dict = None
    while resp_dict is None:
        if attempts > max_attempts:
            raise("The llm did not return a valid response after %s attempts." % max_attempts)
        response =  completion(
            messages=conversation, model=model, api_key=openai_api_key,
            response_format = {"type": "json_object"}
        )
        resp_str = response.choices[0].message.content
        try:
            assert resp_str, "Bot's response is empty."
            start = resp_str.find('{', 0)
            end = resp_str.rfind('}', start)
            resp_str = resp_str[start:end+1]
            resp_dict = json.loads(resp_str, strict = False)
            assert "self_payoff" in resp_dict, "Bot's response does not contain 'self_payoff'."
            assert "other_payoff" in resp_dict, "Bot's response does not contain 'other_payoff'."
            assert "truth" in resp_dict, "Bot's response does not contain 'truth'."
            assert 1 <= resp_dict["self_payoff"] <= 10, "self_payoff score is not between 1 and 10."
            assert 1 <= resp_dict["other_payoff"] <= 10, "other_payoff score is not between 1 and 10."
            assert 1 <= resp_dict["truth"] <= 10, "truth score is not between 1 and 10."
        except (AssertionError, json.JSONDecodeError):
            attempts += 1
            resp_dict = None
            logging.warning(f"Bot's response is not a valid JSON\n{resp_str}\n. Trying again.")
    
    logging.info(f"OpenAI' Chat-GPT response: {resp_dict}")
    return resp_dict

if __name__ == "__main__":
    df = pd.read_csv("data/generated/honesty_2024-06-17_rounds.csv")
    for idx, row in df.iterrows():
        statement = row["reported_amount_reason"]
        scores = classify_response(statement)
        df.loc[idx, "reason_self_payoff"] = scores["self_payoff"]
        df.loc[idx, "reason_other_payoff"] = scores["other_payoff"]
        df.loc[idx, "reason_truth"] = scores["truth"]
    df.to_csv("data/static/honesty_2024-06-17_rounds_classified.csv", index=False) 




