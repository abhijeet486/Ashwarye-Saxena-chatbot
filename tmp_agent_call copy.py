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
# from langroid.mytypes import Document
from langroid.mytypes import DocMetaData
from langroid.parsing.parser import ParsingConfig
from langroid.agent.special.doc_chat_agent import DocChatAgent, DocChatAgentConfig
from langroid.vector_store import QdrantDBConfig, ChromaDBConfig
from langchain_milvus.vectorstores import Milvus
# from langchain_core.documents import Document
from langchain.embeddings import SentenceTransformerEmbeddings
import torch
torch.cuda.set_device(5)
import os
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
torch.cuda.empty_cache()

URI = "./milvus_ash.db"
collection_name = f"collection_ash_{str(4)}"
milvus_vecdb=Milvus(
    # uri=URI,
    collection_name=collection_name,
    drop_old=True,
    auto_id=True,
    embedding_function=SentenceTransformerEmbeddingsConfig(
        model_type="sentence-transformer",
        model_name="BAAI/bge-m3",
    ),
    connection_args={"uri": URI},
)

import weaviate
from langchain_weaviate.vectorstores import WeaviateVectorStore
weaviate_client = weaviate.connect_to_local()

from langchain_core.documents import Document as LangChainDocument
from langroid.mytypes import Document as LangroidDocument, DocMetaData
class CustomDocument:
    def __init__(self, page_content: str, content: str, metadata: DocMetaData):
        self._content = page_content  # Store page_content in a private attribute
        self.content = content  # This can be redundant but left for consistency
        self.metadata = metadata

    @property
    def page_content(self) -> str:
        # This property ensures compatibility with Milvus, which expects 'page_content'
        return self._content
    
    @page_content.setter
    def page_content(self, value: str):
        # Setter method for 'page_content'
        self._content = value

    @property
    def id(self) -> str:
        # Ensure compatibility with LangroidDocument, which might expect an 'id'
        return self.metadata.id

    def __str__(self) -> str:
        # Return a string representation of the document
        return f"CONTENT: {self.content}\nSOURCE: {self.metadata.source}"
    
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
                # vecdb=QdrantDBConfig(
                #     collection_name=collection_name,
                #     replace_collection=True,
                #     # storage_path = "/home/user/chroma-data",
                #     embedding=SentenceTransformerEmbeddingsConfig(
                #         model_type="sentence-transformer",
                #         model_name="BAAI/bge-m3",
                #     ),
                # ),
                parsing=ParsingConfig(
                    splitter=lr.parsing.parser.Splitter.TOKENS,
                    chunk_size=100, # roughly matches LangChain child splitter with 400 chars
                    overlap=40,
                    n_neighbor_ids=2, # At chunking/indexing time, store enough neighbor-doc IDs
                    n_similar_docs=20   ,
                )
            )
    agent = DocChatAgent(agent_cfg)
    agent.vecdb = milvus_vecdb
    path="/raid/home/ihub1/Meghalaya-PSC-Chatbot/test-data"
    docs = []
    for fpath in os.listdir(path):
        # if "service" in fpath.lower() or "csclist" in fpath.lower():
        with open(os.path.join(path,fpath), "r") as f:
            text = f.read()
        print(fpath)
        if fpath=="onlineservices" :
            fpath+= " : this section talks about the various services user can apply for, with their department name, required documents for applying for service, and the Apply and Track link for applying to service and tracking the application. "
        elif fpath=="services_list":
            fpath+= " : this section list the various services by their department name, and also contains information like  Name of Service.  |  Number of working days for service delivery after receipt of application.	|   Department / Organization.  |	Designated Official.    |   Appellate Authority.  |  Whether Service is available Online or Offline "
        # docs.append(Document(content=text, metadata=DocMetaData(source=fpath)))
        docs.append(LangChainDocument(page_content=text, metadata=DocMetaData(source=fpath)))        
        # docs.append(CustomDocument(page_content=text,  content=text, metadata=DocMetaData(source=fpath)))
        # with open("/raid/home/ihub1/Meghalaya-PSC-Chatbot/MSPSDC_TOTAL_PDFS.txt", "r") as f:
    #         text = f.read()
    # docs = [Document(content=text, metadata=DocMetaData(source="MSPSDC - Meghalaya State Public Service Delivery Commission"))]
    # agent.vecdb = milvus_vecdb
    # agent.ingest_docs(docs)
    # agent.vecdb = Milvus.from_documents(
    #     docs,
    #     embedding=SentenceTransformerEmbeddings(
    #         model_name="BAAI/bge-m3",
    #     ),
    #     connection_args={"uri": URI},
    #     drop_old=True,
    # )
    agent.vecdb = WeaviateVectorStore.from_documents(docs, SentenceTransformerEmbeddings(model_name="BAAI/bge-m3"), client=weaviate_client)
    print("\ndone ingesting\n")
    return agent