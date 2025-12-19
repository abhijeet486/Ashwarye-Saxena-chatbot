import os
import warnings
import time
from datetime import datetime, timedelta

import pandas as pd
import torch
import nltk
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain.embeddings import SentenceTransformerEmbeddings

# Configure environment
os.environ['NLTK_DATA'] = '/raid/home/ihub1/nltk_data'
os.environ["TRANSFORMERS_CACHE"] = "/raid/home/ihub1/.cache/huggingface"
os.environ["HF_HOME"] = "/raid/home/ihub1/.cache/huggingface"
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

warnings.filterwarnings('ignore')

# Configure NLTK
print("nltk path", nltk.data.path)
nltk.data.path.insert(0, "/raid/home/ihub1/nltk_data")
nltk.data.path.append("/raid/home/ihub1/nltk_data")
print("new nltk path", nltk.data.path)
nltk.download("punkt")

# Load environment variables
load_dotenv()
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Configure CUDA
if torch.cuda.is_available():
    device = torch.device('cuda:0')  # Use first available GPU
    try:
        torch.cuda.set_device(0)
        torch.cuda.empty_cache()
    except:
        device = torch.device('cpu')
else:
    device = torch.device('cpu')

embeddings = SentenceTransformerEmbeddings(model_name="BAAI/bge-m3")

role_mapping = {
    'system': 'Assistant',
    'user': 'Human'
}

app = FastAPI()


class Query(BaseModel):
    query: str
    message_history: list
    query_type: str = ""


"""
    The query involving(summary questions) should contain descriptive answers(i.e 'response should describe the details'). You have to perform strict check for such user queries.
"""
"""
    If there's no informative information in the response as compared to current query context then return False, but if it contains useful information, return True.
"""

"""
    If user asks quantitative question(how many, List down, how much, what are, ...) the response should answer the required information.
    If user asks qualitative question(summary, details, how to, what is, ...) the response should be descriptive.
"""

def tool_call_html(query):
    pass


from tmp import get_ans


@app.post("/query/")
async def handle_query(query: Query):
    chk_resp = None
    print("in openai_functionality.py")
    all_responses = []
    response, context = get_ans(query.query)
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    response += "\n_NOTE : This information is provided as of " + today.strftime('%d-%m-%Y') + " 12:00 AM" + "_"
    all_responses.append({"role": "system", "content": f"RESPONSE BY RAG: {response}"})
    resp_time = datetime.now().time().isoformat(timespec='milliseconds')
    try:
        data = {
            'question': [query.query],
            'context': [context],
            'response': [response],
            'time' : [resp_time],
        }
    except:
        data = {
            'question': [query.query],
            'context': [""],
            'response': [response],
            'time' : [resp_time],
        }
    try:
        df = pd.read_csv('response_data.csv')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['question', 'context', 'response', "time"])
    df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
    df.to_csv('response_data.csv', index=False)
    return {"response": response, "responses": all_responses, "response_time": resp_time}


@app.get("/")
async def root():
    return {"message": "Service is up!"}


def run():
    uvicorn.run(app, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    run()
