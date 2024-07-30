from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter,TokenTextSplitter, RecursiveCharacterTextSplitter, NLTKTextSplitter

from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings,SentenceTransformerEmbeddings
from langchain import hub
import nltk

from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable.passthrough import RunnableAssign
from operator import itemgetter

from langchain.prompts import ChatPromptTemplate

from langchain_anthropic import ChatAnthropic

import numpy as np
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma

import langroid as lr
from langroid.mytypes import Document
from langroid.mytypes import DocMetaData
from langroid.parsing.parser import ParsingConfig
from langroid.agent.special.doc_chat_agent import DocChatAgent, DocChatAgentConfig
from langroid.vector_store import QdrantDBConfig, ChromaDBConfig
from langroid.embedding_models import OpenAIEmbeddingsConfig
from langroid.utils.configuration import Settings, set_global
from langroid.embedding_models.models import SentenceTransformerEmbeddingsConfig

load_dotenv()
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

files = [
    {
        "name": "mpsc",
        # "path": "/home/ubuntu/python-whatsapp-bot/<name of unstr data file>",
        "path": "complete-data/MSPSDC_TOTAL_DATA.txt",
    }
]


nltk.download('punkt')
loader = TextLoader(files[0]["path"])
pages = loader.load_and_split()

text_splitter  = RecursiveCharacterTextSplitter(
    chunk_size=2000,  # The number of tokens in each chunk
    chunk_overlap=200,  # The number of tokens to overlap between chunks
)
docs = text_splitter.split_documents(pages)
for i, doc in enumerate(docs):
    doc.metadata = {"source": f"{i+1}"}

# vectorstore = FAISS.from_documents(documents=docs, embedding=OpenAIEmbeddings(openai_api_key=""))
# embedding_model = SentenceTransformerEmbeddings(model_name="jinaai/jina-embedding-l-en-v1")

embedding_model = SentenceTransformerEmbeddings(model_name="BAAI/bge-m3")

# Create the Chroma vector store and add documents
vectorstore = FAISS.from_documents(documents=docs, embedding=embedding_model)

# vectorstore = Chroma.from_documents(
#     documents=docs,
#     embedding=embedding_model,
#     collection_name="mpsc_collection",
#     persist_directory="chroma_data"
# )


retriever = vectorstore.as_retriever()

llm = ChatAnthropic(model="claude-3-haiku-20240307", temperature=1)

def format_docs(docs):
    formatted_docs =  "\n\n".join(doc.page_content for doc in docs)
    sources = [doc.metadata.get("source", "unknown") for doc in docs]
    return formatted_docs,sources

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Hey there, Claude! As an assistant for Meghalaya State Public Services Delivery Commission (MSPSDC), I need your help. I want you to handle queries from users about MSPSDC or Meghalaya State Public Services Delivery Commission. Please respond by drawing from the knowledge you've been provided in the context, external information, and your general knowledge pertinent to MSPSDC. Please decline to answer queries that are not related to MSPDC. If you're unsure about an answer, it's okay to decline and state that you can only help with queries related to MSPDC.

For the Hi, Hello and greetings, reply to messages similar to following and please rephrase it before sending:
"Welcome to the MSPSDC Chatbot! 🎉 Hello there! I'm your experimental AI companion designed to assist you with any queries you may have about MSPSDC. If you are here to inquire about Meghalaya State Public Services, feel free to ask me anything. While I'm still learning and evolving, I'll do my best to provide you with helpful information and guidance. So, don't hesitate to fire away your questions, and let's embark on this experimental journey together!"

Please respond in the same language as asked, translate if needed, and the set of languages is English and Indian languages.

You are made by iHUb-Anubhuti-IIITD Foundation. Do not mention GPT or OpenAI.
Here are the links which should be appended to the responses based on the query related to About Us: https://mspsdc.meghalaya.gov.in/aboutus.htm, contact: https://mspsdc.meghalaya.gov.in/contactus.htm, tenders: https://mspsdc.meghalaya.gov.in/tenders.htm, Services: https://mspsdc.meghalaya.gov.in/services_list.htm, Services Apply: https://mspsdc.meghalaya.gov.in/onlineservices.htm, Notifications: https://mspsdc.meghalaya.gov.in/notification.htm, Presentations: https://mspsdc.meghalaya.gov.in/presentations.htm, Function & Duties: https://mspsdc.meghalaya.gov.in/functions.htm, Review Meetings: https://mspsdc.meghalaya.gov.in/reviewmeetings.htm, Home: https://mspsdc.meghalaya.gov.in/index.htm

Please do not manufacture URLs on your own. Do not respond with "Welcome to chatbot" message if the user does not send a greeting message.

Please make the responses elaborate.
"""
            "\n{context}\n"
            """Respond based on the document and the external knowledge about Meghalaya State Public Services Delivery Commission (MSPSDC) only.""",
        ),
        ("human", "{question}"),
    ]
)

response_generator = (prompt | llm | StrOutputParser()).with_config(
    run_name="GenerateResponse",
)

chain = (
    RunnableAssign(
        {
            "context": (itemgetter("question") | retriever | format_docs).with_config(
                run_name="FormatDocs"
            )
        }
    )
    | response_generator
)

# embedder = OpenAIEmbeddings(openai_api_key="")

# def find_relevant_docs(query, top_n=5, threshold=0.5):
#     # query_vector = embedder.embed_query(query)
#     results = vectorstore.similarity_search_with_score(query, k=top_n)
    
#     relevant_docs = []
#     relevant_indices = []
#     for i, (doc, score) in enumerate(results):
#         if score < threshold:
#             relevant_indices.append((i, doc, score))
#     return relevant_indices

# Example usage
# query = "Tell me the order dated September 2024 and their designations."
# relevant_docs = find_relevant_docs(query)

# if relevant_docs:
#     print(f"Found {len(relevant_docs)} relevant documents:")
#     for idx, doc, score in relevant_docs:
#         print(f"Document: {idx}, Similarity Score: {score}")
#         print(doc.page_content)
#         time.sleep(5)
# else:
#     print("No relevant documents found.")
def retrieve_context(question):
    retrieved_docs = retriever.invoke(question)
    print("\n\nQuestion:", question)
    for doc in retrieved_docs:
        print(f"Source: {doc.metadata['source']}")
        print(f"Content: {doc.page_content[:500]}...") 
        print("\n")
    docs = retriever.get_relevant_documents(question)
    # print("Retrieved Documents:", docs)
    formatted_docs, sources = format_docs(docs)
    return formatted_docs, sources

def process_unstr_query(query): 
    try:
        context, sources = retrieve_context(query)
        # print("Document Context:", context)
        # print("Document Sources Used:", sources)
        response = chain.invoke({"question": query})
        print("Response:", response)
        return response
    except Exception as e:
        print("Error:", e)
        return "HI! I am experiencing some dizziness. Please give me a few minutes to fix myself."
query = " what are all the services available ? "
print(process_unstr_query(query))
# from datetime import datetime
# current_date = datetime.now()
# formatted_date = current_date.strftime('%d-%m-%Y')
# print(formatted_date)
# import pandas as pd
# df = pd.read_csv('/home/ihub1/Meghalaya-PSC-Chatbot/MeghalayaQueries - Running-2.csv')
# print(df.columns)
# ls = df.columns
# df = df.drop(columns= [column for column in ls if 'Unnamed' in column])
# df = df.dropna(subset=['EXPECTED OUTPUT'])
# df[f"Response on {formatted_date}"] = df.apply(lambda row: process_unstr_query(row['Question']), axis=1)

# df.to_excel('answer.xlsx', index=False)