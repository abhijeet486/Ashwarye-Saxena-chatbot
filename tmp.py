import os
from openai import OpenAI
import warnings
warnings.filterwarnings('ignore')
import time
import nltk
import os
os.environ['NLTK_DATA'] = '/raid/home/ihub1/nltk_data'
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
import pandas as pd
# Meghalaya-PSC-Chatbot/test-data/services_list
# nltk.download("punkt")
# %pip install  anthropic
# %pip install sentence_transformers
# %pip install langroid[hf-embeddings]

from langroid.mytypes import Document
from langroid.mytypes import DocMetaData
import anthropic

from dotenv import load_dotenv
load_dotenv()
os.environ['NLTK_DATA'] = '/raid/home/ihub1/nltk_data'

# client = OpenAI()
import torch
torch.cuda.set_device(3)
torch.cuda.empty_cache()

# client = anthropic.Anthropic()
# client = OpenAI()
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

llmc = ChatOllama(model="llama3")
lllm = Ollama(
    model="llama3:70b"
)

from tmp_agent_call import GetAgent
agent = GetAgent()

def get_ans(query):
    torch.cuda.empty_cache()
    torch.cuda.set_device(3)
    torch.cuda.empty_cache()
    torch.cuda.set_device(7)
    question = query
    
    # print(question)
    print("Query..", question)
    agent.clear_history(0)
    t1 = time.time()
    chunks = agent.get_relevant_chunks(question)
    print("Time for search... ", time.time() - t1)
    
    
    chunks = [("section begins doc_id: "+ chunks[0].dict()['metadata']['source'] + " :\n"+ (x.dict()['content'])) +" above section ends\n" for x in chunks]
    # chunks = [(x.dict()['content']) for x in chunks]
    
    prompt ="""Given the content and question below, extract the relevant paragraphs of content that are relevant to answering the question (if such text exists). Use these extracts to answer the question. Do not make up an answer. Only use the content given even if it contradicts your knowledge. Use reasoning to infer composite question answers from the content.

Hey there! As an assistant for the complaints forum, I need your help. I want you to handle queries from users about their complaints. Please respond by drawing from the knowledge you've been provided in the context, external information, and your general knowledge pertinent to handling complaints. Please decline to answer queries that are not related to complaint handling. If you're unsure about an answer, it's okay to decline and state that you can only help with queries related to complaint handling.

For greetings, respond with a message similar to the following, and please rephrase it before sending:
"Welcome to the Complaints Forum Chatbot! 🎉 Hello there! I'm your experimental AI companion designed to assist you with any queries you may have about submitting and categorizing complaints. If you are here to file a complaint, feel free to ask me anything. While I'm still learning and evolving, I'll do my best to provide you with helpful information and guidance. So, don't hesitate to fire away your questions, and let's embark on this experimental journey together!"

Please respond in the same language as the query, translating if needed. The supported languages are English and Indian languages.

You are created by iHUb-Anubhuti-IIITD Foundation. Do not mention GPT or OpenAI.

Here are some key points for your responses based on the query:
- Detect sentiments from the user query and the whole chat in order to categorize complaints into predefined categories.
- Clarify complaint details by asking follow-up questions to ensure accurate categorization.
- Provide relevant links or information if needed to assist with complaint submission.
- In case of user asking about complaints process or providing a complaint about something, classify the complaints appropriately and tune the responses towards complaints clarification.


Do not create URLs on your own. Do not respond with the "Welcome to chatbot" message if the user does not send a greeting.

Do not use the following phrases: ["Based on information provided in the content/context", "According to information provided", "According to documents/context provided", "Based on information/context/document provided"]. Just output the answer.

Make responses elaborate. If you don't have enough information regarding the query, check the related link and retrieve the correct data from it.

Keep the response focused on handling complaints, such as clarifying details, categorizing complaints, and providing information related to the complaints process. Provide information corresponding to the complaints forum only.

Remember numbers or numericals provided in the context intelligently so you can answer questions related to them if needed. For example, if the query mentions numbers such as year/complaint number, provide the answer corresponding to that number only.""".strip()

    context = "\n--\n".join(chunks)
    query = f"""Context:
    {context}
    Question: {question}
    Answer:
    """
    with open("debug_path_abhijeet", "a+") as f : 
        f.write(query)
        system_prompt  = prompt
        messages = [
            SystemMessage(
                content = system_prompt
            ),
            HumanMessage(
                content=query
            )
        ]

        chat_model_response = lllm.invoke(messages)
        print("\n\nfrom messages", chat_model_response)
        f.write("\n\nfrom messages" + chat_model_response)
        
        # print("\n\nfrom messages", chat_model_response.content)
        # chainprompt = ChatPromptTemplate.from_template("""Context : \n```\n{context} \n``` \n System : You need to follow the below instructions carefully and answer the query straight-forwardly\n``` \n {system} \n``` \n Query : ``` \n {human} \n``` \n Answer : // YOUR ANSWER TO ABOVE QUERY in Qeury : ```... ``` using Context : ``` ... ```// """)
        chainprompt = ChatPromptTemplate.from_template("""Context : \n```\n{context} \n``` \n System : You need to follow the below instructions carefully and answer the query straight-forwardly\n``` \n {system} \n``` \n Query : ``` \n {human} \n``` \n Answer : // YOUR ANSWER TO ABOVE QUERY in Qeury : ```... ``` using Context : ``` ... ```// """)

        chain = chainprompt | llmc | StrOutputParser()

        print("\n\nfrom chain", chain.invoke({"system" : system_prompt, "context": context, "human" : question}))
        f.write("\n\nfrom chain\n"+ chain.invoke({"system" : system_prompt, "context": context, "human" : question}))
        
        llama3_template="""
        <|begin_of_text|>
        <|start_header_id|>system<|end_header_id|>
        {system}
        <|eot_id|>
        <|start_header_id|>user<|end_header_id|>
        {context}
        <|eot_id|>
        <|start_header_id|>assistant<|end_header_id|>
        Okay, I've taken note of above context. I'll keep this in mind as we continue our conversation. What's your next question or topic you'd like to discuss?
        <|eot_id|>
        <|start_header_id|>user<|end_header_id|>
        Look at the system instructions and context from user carefully and resolve the user response which should be correct and complete.
        User : {query}
        <|eot_id|>
        <|start_header_id|>assistant<|end_header_id|>
        """

        llama3_prompt = ChatPromptTemplate.from_template(llama3_template)
        llama3_chain = llama3_prompt | lllm |  StrOutputParser()
        llama3_response = llama3_chain.invoke({"system" : system_prompt, "context": context, "query" : question})
        print("\n\nfrom llama3 chain with tokens : ", llama3_response)
        f.write("\n\nfrom llama3 chain with tokens : \n" + llama3_response)
        verify_template = llama3_template + """
        {assistant}
        <|eot_id|>
        <|start_header_id|>user<|end_header_id|>
        Now looking at the Context, User Query and above Assistant Response, tell me if the response is correct. Also mention the correct answer from the context for the user query.
        <|eot_id|>
        <|start_header_id|>assistant<|end_header_id|>
        """
        verify_prompt = ChatPromptTemplate.from_template(verify_template)
        verify_chain = verify_prompt | lllm | StrOutputParser()
        verify_response = verify_chain.invoke({"system" : system_prompt, "context": "\n".join(chunks[::-1]), "query" : question, "assistant" : llama3_response})
        print("\n\nfrom llama3 chain verification : ", verify_response)
        f.write("\n\nfrom llama3 chain verification : \n" + verify_response)
        return llama3_response, verify_response
# while(True):
#     usr_q = input("YOUR QUESTION HERE : ",)
#     if(usr_q.lower()=="exit"):
#         break
#     get_ans(usr_q)
# df = pd.read_csv("/raid/home/ihub1/Meghalaya-PSC-Chatbot/MeghalayaQueries - QuestionsOnly copy.csv")
# df[['Llama3_Response', 'Verify_Response']] = df['Questions'].apply(lambda question: pd.Series(get_ans(question)))
# df.to_csv("LLAMA3_Responses_verified_on_services.csv",index=False)