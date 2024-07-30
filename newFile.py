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

# device = torch.device('cuda:1' if torch.cuda.is_available() else 'cpu')
import torch
torch.cuda.set_device(4)

import os
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
torch.cuda.empty_cache()

collection_name = f"collection-{str(4)}"
path = "/raid/home/ihub1/Meghalaya-PSC-Chatbot/MSPSDC_TOTAL_PDFS.txt"
with open(path, "r") as f:
    text = f.read()
docs = [Document(content=text, metadata=DocMetaData(source="user"))]
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
                    # replace_collection=True,
                    # storage_path = "/home/user/chroma-data",
                    embedding=SentenceTransformerEmbeddingsConfig(
                        model_type="sentence-transformer",
                        model_name="BAAI/bge-m3",
                    ),
                ),
                parsing=ParsingConfig(
                    splitter=lr.parsing.parser.Splitter.TOKENS,
                    chunk_size=100, # roughly matches LangChain child splitter with 400 chars
                    overlap=20,
                    n_neighbor_ids=2, # At chunking/indexing time, store enough neighbor-doc IDs
                    n_similar_docs=20   ,
                )
            )


    agent = DocChatAgent(agent_cfg)
    agent.ingest_docs(docs)
    return agent
