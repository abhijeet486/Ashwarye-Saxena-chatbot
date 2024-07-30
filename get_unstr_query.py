import os


from openai import OpenAI
import warnings
warnings.filterwarnings('ignore')
import time
import nltk
import os
os.environ['NLTK_DATA'] = '/raid/home/ihub1/nltk_data'
import json

# nltk.download("punkt")
# %pip install  anthropic
# %pip install sentence_transformers
# %pip install langroid[hf-embeddings]

from langroid.mytypes import Document
from langroid.mytypes import DocMetaData
import anthropic

from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = ""
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")
os.environ['NLTK_DATA'] = '/raid/home/ihub1/nltk_data'

# client = OpenAI()
import torch
# torch.cuda.set_device(6)
client = anthropic.Anthropic()

from newFile import GetAgent
agent = GetAgent()

system_prompt ="""Given the content and question below, extract the relevant paragraphs  of
    content that is relevant to answering the question (if such text exists). Use these extracts to answer the question. Do not 
    make up an answer. Only use the content given even if it contradicts your knowledge. Use reasoning to infer composite question answers from the content.
    
    Hey there, Claude! As an assistant for Meghalaya State Public Services Delivery Commission (MSPSDC), I need your help. I want you to handle queries from users about MSPSDC or Meghalaya State Public Services Delivery Commission. Please respond by drawing from the knowledge you've been provided in the context, external information, and your general knowledge pertinent to MSPSDC. Please decline to answer queries that are not related to MSPDC. If you're unsure about an answer, it's okay to decline and state that you can only help with queries related to MSPDC.

For the Hi, Hello and greetings, reply to messages similar to following and please rephrase it before sending:
"Welcome to the MSPSDC Chatbot! 🎉 Hello there! I'm your experimental AI companion designed to assist you with any queries you may have about MSPSDC. If you are here to inquire about Meghalaya State Public Services, feel free to ask me anything. While I'm still learning and evolving, I'll do my best to provide you with helpful information and guidance. So, don't hesitate to fire away your questions, and let's embark on this experimental journey together!"

Please respond in the same language as asked, translate if needed, and the set of languages is English and Indian languages.

You are made by iHUb-Anubhuti-IIITD Foundation. Do not mention GPT or OpenAI.
Here are the links which should be appended to the responses based on the query related to About Us: https://mspsdc.meghalaya.gov.in/aboutus.htm, contact: https://mspsdc.meghalaya.gov.in/contactus.htm, tenders: https://mspsdc.meghalaya.gov.in/tenders.htm, Services: https://mspsdc.meghalaya.gov.in/services_list.htm, Services Apply: https://mspsdc.meghalaya.gov.in/onlineservices.htm, Notifications: https://mspsdc.meghalaya.gov.in/notification.htm, Presentations: https://mspsdc.meghalaya.gov.in/presentations.htm, Function & Duties: https://mspsdc.meghalaya.gov.in/functions.htm, Review Meetings: https://mspsdc.meghalaya.gov.in/reviewmeetings.htm, Home: https://mspsdc.meghalaya.gov.in/index.htm

Please do not manufacture URLs on your own. Do not respond with "Welcome to chatbot" message if the user does not send a greeting message. 

Very Strictly Don't output following phrases: ["Based on information provided in the content/context", "According to information provided", "According to documents/context provided", "Based on information/context/document provided"]. Just output the answer.

Please  make the responses elaborate and if you didn't enough information regarding the query, please once check the link related to the query and retreive correct data from that link. 

Keep the response around MSPSDC only such as contacts, notifications, review meetings or tenders. Please provide the information corresponding to MSPSDC only. 

Remember NUMBERS or Numericals provided in the context so intelligently that you can answer and Remember to use them in the answer related to them if needed. for example if the query mentions numbers such as year / tender no / notification no , provide answer corresponding to that number only.

Please include the source also from where the information is used. Provide source in a format such as " There is one tender ( http://mspsdc.meghalaya.gov.in/tenders.htm ) " or "Shri. M.S.Rao, IAS (Retd) is the Chief Commissioner and head of the Meghalaya State Public Services Delivery Commission (MSPSDC).[1] .... [1]( http://mspsdc.meghalaya.gov.in/contactus.htm ) " etc. Use similar kind of format to provide source of information in the end of Answer. Ensure there is proper spacing before and after that link.
   """.strip()

# install -> pip install -q -U google-generativeai

"""
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel(
        model_name = 'gemini-1.5-flash',
        system_instruction = system_prompt
    )
"""

def investAgent(agent,path="/raid/home/ihub1/Meghalaya-PSC-Chatbot/MSPSDC_TOTAL_PDFS.txt"):
    with open(path, "r") as f:
        text = f.read()
    docs = [Document(content=text, metadata=DocMetaData(source="user"))]
    agent.ingest(docs)

def get_context(query):
    torch.cuda.empty_cache()
    torch.cuda.set_device(4)
    torch.cuda.empty_cache()
    # torch.cuda.set_device(6)
    question = query
    agent.clear_history(0)
    chunks = agent.get_relevant_chunks(question)
    chunks = [("doc_id: "+ chunks[0].dict()['metadata']['source'] + " | "+ (x.dict()['content'])) for x in chunks]
    context = "\n--\n".join(chunks)
    return context

def get_ans(query):
    global system_prompt

    torch.cuda.empty_cache()
    torch.cuda.set_device(4)
    torch.cuda.empty_cache()
    # torch.cuda.set_device(6)
    question = query
    
    print(question)
    print("Query..", question)
    agent.clear_history(0)
    t1 = time.time()
    chunks = agent.get_relevant_chunks(question)
    print("Time for search... ", time.time() - t1)
    
    
    chunks = [("doc_id: "+ chunks[0].dict()['metadata']['source'] + " | "+ (x.dict()['content'])) for x in chunks]


    context = "\n--\n".join(chunks)
    query = f"""Content:
    {context}
    Question: {question}
    Answer: 
    """

    # print(context)
    # chat_completion = client.chat.completions.create(
    #     messages=[
    #                 {"role": "system", "content": system_prompt},
    #                 {"role": "user", "content": query}
    #             ],
    #     # model="gpt-4",
    #     model="gpt-4-1106-preview",
    # )


    

    """
    messages=[
        {
            "role": "user",
            "parts": [
                {
                    "text": query
                }
            ]
        }
    ]
    response = model.generate_content(messages, generation_config = genai.types.GenerationConfig(temperature=0))
    ans = response.text

    with open('temp_gemini.txt', 'a') as f:
        f.write(f"query ----------- \n\n{question}\n\n")
        f.write(f"chunks ----------- \n\n{chunks}\n\n")
        f.write(f"ans ----------- \n\n{ans}\n\n")
        f.write(f"stop reason : {response.candidates[0].finish_reason} \n\n" )
        f.write(f"usage : I : {response.usage_metadata.prompt_token_count} O : {response.usage_metadata.candidates_token_count} ")
    """

    chat_completion = client.messages.create(
        # model="claude-3-opus-20240229",
        model="claude-3-haiku-20240307",
        # model = "claude-3-5-sonnet-20240620",
        max_tokens=4096,
        temperature=0,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    }
                ]
            }
        ]
    )
    # ans = lllm.invoke(system_prompt + "\n" + query)
    # ans = chat_completion.choices[0].message.content

    ans = chat_completion.content[0].text


    with open('temp.txt', 'a') as f:
        f.write(f"query ----------- \n\n{question}\n\n")
        f.write(f"chunks ----------- \n\n{chunks}\n\n")
        f.write(f"ans ----------- \n\n{ans}\n\n")
        f.write(f"stop reason : {chat_completion.stop_reason} \n\n" )
        f.write(f"usage : I : {chat_completion.usage.input_tokens} O : {chat_completion.usage.output_tokens} ")

    with open("tokenCount.json", 'r') as file:
        dataT = json.load(file)
    
    dataT["total_ip_tokens"] += chat_completion.usage.input_tokens
    dataT["total_op_tokens"] += chat_completion.usage.output_tokens

    dataT["queries_count"] += 1

    dataT["avg_ip_tokens"] = dataT["total_ip_tokens"]/dataT["queries_count"]
    dataT["avg_op_tokens"] = dataT["total_op_tokens"]/dataT["queries_count"]

    with open("tokenCount.json", 'w') as file:
        json.dump(dataT, file, indent=4)

    return ans, context

