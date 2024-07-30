from fastapi import FastAPI, logger
from pydantic import BaseModel
import sqlite3
import pandas as pd
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent, SQLDatabaseToolkit
from langchain_anthropic import ChatAnthropic

import os
from dotenv import load_dotenv
import uvicorn
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import SentenceTransformerEmbeddings

from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from constants import table_schema
from tablesMetaData import tables_meta_data
import torch

from anthropic import Anthropic, AsyncAnthropic
from openai import OpenAI
import nltk
# from handle_unstr_query import process_unstr_query, retrieve_context
import os
import pandas as pd

os.environ['NLTK_DATA'] = '/raid/home/ihub1/nltk_data'


from langroid.language_models.openai_gpt import OpenAIChatModel, OpenAIGPTConfig


from langroid.embedding_models.models import SentenceTransformerEmbeddingsConfig


import warnings
warnings.filterwarnings('ignore')
import nltk

#nltk.download("punkt")
import os


os.environ["TRANSFORMERS_CACHE"] = "/raid/home/ihub1/.cache/huggingface"
os.environ["HF_HOME"]="/raid/home/ihub1/.cache/huggingface"
print("nltk path", nltk.data.path)
nltk.data.path.insert(0, "/raid/home/ihub1/nltk_data")
nltk.data.path.append("/raid/home/ihub1/nltk_data")
os.environ['NLTK_DATA'] = '/raid/home/ihub1/nltk_data'
print("new nltk paht", nltk.data.path)
nltk.download("punkt")
# nest_asyncio.apply()
import langroid as lr
from langroid.mytypes import Document
from langroid.mytypes import DocMetaData
from langroid.parsing.parser import ParsingConfig
from langroid.agent.special.doc_chat_agent import DocChatAgent, DocChatAgentConfig
from langroid.vector_store import QdrantDBConfig, ChromaDBConfig

# device = torch.device('cuda:1' if torch.cuda.is_available() else 'cpu')
import torch


import os
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
torch.cuda.empty_cache()

from datetime import datetime
nltk.data.path.append("/raid/home/ihub1/")
load_dotenv()
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["TRANSFORMERS_CACHE"] = "/raid/home/ihub1/.cache/huggingface"
os.environ["HF_HOME"]="/raid/home/ihub1/.cache/huggingface"

device = torch.device('cuda:1' if torch.cuda.is_available() else 'cpu')
torch.cuda.set_device(2)

embeddings = SentenceTransformerEmbeddings(model_name="BAAI/bge-m3")

role_mapping = {
    'system': 'Assistant',
    'user': 'Human'
}

app = FastAPI()
# MEMORY_KEY = "chat_history"
# full_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are very powerful assistant that answers user questions",
#         ),
#         SystemMessagePromptTemplate(prompt=few_shot_prompt),
#         MessagesPlaceholder(variable_name=MEMORY_KEY),
#         ("human", "{input}"),
#         MessagesPlaceholder("agent_scratchpad"),
#     ],
# )


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




import time


# from get_unstr_query import get_ans, get_context
from tmp import get_ans
from datetime import datetime, timedelta

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
