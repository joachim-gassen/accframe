import botex
import os
import dotenv


url = "http://exp.trr266.de/InitializeParticipant/o1sctetl"
dotenv.load_dotenv("secrets.env")
openai_api_key = os.getenv("OPENAI_API_KEY")

botex.run_bot(  
    botex_db="data/generated/botex_db.sqlite3",     
    session_id="iws973ub",
    openai_api_key=openai_api_key,
    url = url
)