from langroid.language_models.openai_gpt import OpenAIChatModel, OpenAIGPTConfig
from langroid.embedding_models.models import SentenceTransformerEmbeddingsConfig
import warnings
warnings.filterwarnings('ignore')
#import nltk
#nltk.download("punkt")
import os
os.environ["TRANSFORMERS_CACHE"] = os.getcwd()
os.environ["HF_HOME"]="/raid/home/ihub1/.cache/huggingface"
#nltk.data.path.append("/raid/home/ihub1/")

os.environ['NLTK_DATA'] = '/raid/home/ihub1/nltk_data'

# nest_asyncio.apply()
import langroid as lr
from langroid.mytypes import Document
from langroid.mytypes import DocMetaData
from langroid.parsing.parser import ParsingConfig
from langroid.agent.special.doc_chat_agent import DocChatAgent, DocChatAgentConfig
from langroid.vector_store import QdrantDBConfig, ChromaDBConfig
import torch
torch.cuda.set_device(5)
import os
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
torch.cuda.empty_cache()

collection_name = f"collection_ash_{str(4)}"

import pandas as pd

# Read the CSV file into a DataFrame
csv_file_path = '/raid/home/ihub1/ash-tmp/complaints.csv'
df = pd.read_csv(csv_file_path)

# Function to render DataFrame in the specified text format
def render_dataframe(df):
    result = []
    for index, row in df.iterrows():
        row_text = []
        for col in df.columns:
            row_text.append(f"{col} : {row[col]}")
        result.append(f"Row({index}): {' | '.join(row_text)}")
    return "\n".join(result)

def GetAgent():
    agent_cfg = DocChatAgentConfig(
                stream = False,
                use_fuzzy_match = True,
                llm = OpenAIGPTConfig(
                    type="openai",
                    chat_model=OpenAIChatModel.GPT4_TURBO,
                    completion_model=OpenAIChatModel.GPT4_TURBO,
                    timeout=40,
                    ),
                cross_encoder_reranking_model = "",
                n_neighbor_chunks=2, # retrieve 1 neighboring chunk on either side of matching chunk
                vecdb=QdrantDBConfig(
                    collection_name=collection_name,
                    replace_collection=True,
                    # storage_path = "/home/user/chroma-data",
                    embedding=SentenceTransformerEmbeddingsConfig(
                        model_type="sentence-transformer",
                        model_name="BAAI/bge-m3",
                    ),
                ),
                parsing=ParsingConfig(
                    splitter=lr.parsing.parser.Splitter.TOKENS,
                    chunk_size=100, # roughly matches LangChain child splitter with 400 chars
                    overlap=40,
                    n_neighbor_ids=2, # At chunking/indexing time, store enough neighbor-doc IDs
                    n_similar_docs=20   ,
                )
            )

    agent = DocChatAgent(agent_cfg)
    # path="/raid/home/ihub1/Meghalaya-PSC-Chatbot/test-data"
    # docs = []
    # for fpath in os.listdir(path):
    #     # if "service" in fpath.lower() or "csclist" in fpath.lower():
    #     with open(os.path.join(path,fpath), "r") as f:
    #         text = f.read()
    #     print(fpath)
    #     if fpath=="onlineservices" :
    #         fpath+= " : this section talks about the various services user can apply for, with their department name, required documents for applying for service, and the Apply and Track link for applying to service and tracking the application. "
    #     elif fpath=="services_list":
    #         fpath+= " : this section list the various services by their department name, and also contains information like  Name of Service.  |  Number of working days for service delivery after receipt of application.	|   Department / Organization.  |	Designated Official.    |   Appellate Authority.  |  Whether Service is available Online or Offline "
    #     docs.append(Document(content=text, metadata=DocMetaData(source=fpath)))
    # with open("/raid/home/ihub1/Meghalaya-PSC-Chatbot/MSPSDC_TOTAL_PDFS.txt", "r") as f:
    #         text = f.read()
    docs = [Document(content=render_dataframe(df), metadata=DocMetaData(source="Complaints dataset"))]
    agent.ingest_docs(docs)
    print("\ndone ingesting\n")
    return agent

