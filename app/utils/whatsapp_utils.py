import logging
from flask import current_app, jsonify
import json
import requests
import random
import re
# from openai import OpenAI, AsyncOpenAI
from anthropic import Anthropic
import threading
import time
import datetime
import sqlite3


whatsapp_recepient_question_set = {}
slack_recepient_question_set = {}

general_response = "I am a helpful AI based Chatbot for Meghalaya State Public Services Delivery Commission (MSPSDC)"
preprocess_responses = ["Got it! Let me find information about it...", "Processing...", "Working on it...",
                        "Fetching...", "Getting your results for you...",
                        "Let me check that out for you...", "Searching...",
                        "Alright! Let me look into that query for you..."]




def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


def generate_response(user_id, query, query_type, message_history, msg_system, channel_id=None):
    print(f"INPUT FOR app.py and openai: {query}")
    send_msg = "I apologize! There seems to be a backend issue. Can you please ask another query?"
    # send_msg = "I'm undergoing some maintainence! I'll be back online on Saturday. In case you any emergency, you can contact iHub Anubhuti team or call at +91 9306024352"

    url = 'http://127.0.0.1:5000/query/'
    headers = {'Content-Type': 'application/json'}
    json_message = {"query": query, "message_history": message_history, "query_type":query_type}
    query_json = json.dumps(json_message)

    response = None

    class TimeoutException(Exception):
        pass

    def fetch_response():
        nonlocal response
        try:
            response = requests.post(url, data=query_json, headers=headers, timeout=600)
        except requests.Timeout:
            raise TimeoutException("API request timed out")
 
    # Start the API request in a separate thread
    api_thread = threading.Thread(target=fetch_response)
    api_thread.start()

    wait_time = 60
    trials = 3
    while api_thread.is_alive():
        if query_type == "greeting":
            continue
        elif wait_time % 60 == 0 and trials != 0:
            trials -= 1
            # Send an intermediate message to the user
            intermediate_messages = [
                "Hold on, I'm fetching the results for you.",
                "Please wait a moment, I'm retrieving the information.",
                "Fetching data, just a moment please.",
                "Almost done!",
                "Please hold on while I fetch your results.",
                "Almost done fetching, don't go away!",
                "Fetching data, appreciate your patience!",
                "Getting your data, thank you for waiting!"
            ]
            intermediate_message = random.choice(intermediate_messages)
            translated_msg = intermediate_message
            # translated_msg = translate(query, intermediate_message)

            translated_msg_parts = translated_msg.split("\n")
            msg_to_be_sent = translated_msg_parts[-1].split(":")[-1].strip()

            if msg_system == "wp":
                send_response = get_text_message_input(user_id, msg_to_be_sent)
                send_message(send_response)
            else:
                send_response_to_slack(channel_id, msg_to_be_sent, user_id)

        time.sleep(1)
        wait_time -= 1

    # If API thread is still running, it means it hasn't completed within 2 minutes
    if api_thread.is_alive():
        # Terminate the thread
        api_thread.join()
        if msg_system == "wp":
            send_response = get_text_message_input(
                user_id,
                send_msg
            )
            send_message(send_response)
        else:
            send_response_to_slack(channel_id, send_msg, user_id)
        resp_time = datetime.datetime.now().time().isoformat(timespec='milliseconds')
        return send_msg, None, resp_time

    # API request completed within the timeout
    if response.status_code == 200:
        # Print the response content
        print("RESPONSE FROM THE SERVER AT 5000 PORT:", response.json())
        return response.json()["response"], response.json()["responses"], response.json()["response_time"]
    else:
        print("FAILED TO GET A RESPONSE FROM THE SERVER AT 5000 PORT, status code:", response.status_code)
        if msg_system == "wp":
            send_response = get_text_message_input(
                user_id,
                send_msg
            )
            send_message(send_response)
        else:
            send_response_to_slack(channel_id, send_msg, user_id)
        resp_time = datetime.datetime.now().time().isoformat(timespec='milliseconds')
        return send_msg, None, resp_time


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    print(data)

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code.
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except requests.HTTPError as http_err:
        # Extract error details from the response
        error_details = response.json()  # Assuming the error details are in JSON format
        logging.error(f"HTTP error occurred: {http_err} - Details: {error_details}")
        # Return or log the detailed error message for further investigation
        return jsonify({"status": "error", "message": "HTTP error", "details": error_details}), 500
    except requests.RequestException as req_err:
        # This will catch any general request exception
        logging.error(f"Request failed due to: {req_err}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)  # Make sure you have this function defined to handle logging
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def is_general_question(message):
    content = f"""You need to check if the query contains any of the general questions from the list given or even 
    similar questions. The query can be in any language, you need to check if the query is in the same context. You need
    to respond with  True or False accordingly.
    general_questions = ["What's up", "What's your role", "What can you do", "What is your role", "Who are you",
             "What’s your purpose", "What is your purpose", "What can you do", "What are you doing", "What're you doing"]

    Text: {message}
    Class: """

    client = Anthropic()
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        temperature=0.6,
        system = "You are a computer system which only gives boolean response i.e. True or False for checking if the query is a general question.",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": content}
        ]
    )
    print(f"IS GENERAL QUESTION: {response.content[0].text}")
    return response.content[0].text


def check_message_type(message):
    content = f"""Classify the text into one of the classes. The text can be user query or greeting in any language, you need
    to identify and tell me for any language if the message is a greeting or a query.
    Classes: [`greeting`, `query`]

    Text: {message}
    Class: """

    client = Anthropic()
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        temperature=0.6,
        system = "You are a computer system which only gives binary response. answer one word: either 'greeting' or 'query'",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": content}
        ]
    )
    print("/-"*10)
    print(f"MESSAGE TYPE: {response.content[0].text}")
    print("/-"*10)

    return response.content[0].text


def translate(query, eng_message):
    content = f"""You need to convert my english message to the same language as that of the query asked by the user provided below. 
    Provide me the translated message. Provide me just the detected language of the query and the accurately translated 
    message of the english message provided. The set of languages is 
    english and indian languages. If the detected language is english, return me the message as it is. Be very accurate 
    as this impacts user experience. 
    
    Query = {query}
    English Message: {eng_message}
    Message in detected language: """

    client = Anthropic()
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        temperature=0.6,
        max_tokens=4096,
        messages=[
            {"role": "user", "content": content}
        ]
    )
    print("-"*50)
    print(f"Query = {query} English Message: {eng_message}")
    print(f"TRANSLATION: {response.content[0].text}")
    print("-"*50)

    return response.content[0].text

#TODO fix later
def refine_query(query, message_history):
    content = f"""You need to refine and format the question properly in the same language is user question is in. Refinement should be
    in such a way that sending it to a chatbot makes it able to understand the question correctly in terms of MSPSDC components 
    like Presentations, Departments, Review Meetings, Notifications, Tenders, Contacts and Designation asking it to provide these from the database. 
    If there is one of these already mentioned, don't mention all the words, refine question with only the context that is provided in the question.
    Make sure to not expand the context in the user question, match the context as it is.
    and provide the results. Make sure that no context from the user question should be lost considering the message history. 
    If there are multiple things asked, break it down to multiple questions so that each question is addressed.
    Provide me just the refined question to be passed to the RAG pipeline in the same language.

    Question = {query}
    Message History: {message_history}
    Refined Question: """

    client = Anthropic()
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        temperature=0.6,
        system="You are an English professor. You need to parse the user question and return the question in proper English.",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": content}
        ]
    )
    print("*"*50)
    # print(content)
    print(f"Refined query: {response.content[0].text}")
    print("*"*50)

    return response.content[0].text


def unix_to_datetime(unix_timestamp):
    # Convert Unix timestamp to datetime object
    return datetime.datetime.utcfromtimestamp(unix_timestamp)


def is_within_tolerance(unix_timestamp, tolerance_seconds=3):
    # Get current datetime in UTC
    current_utc_time = datetime.datetime.utcnow()

    # Convert Unix timestamp to datetime object
    target_datetime = unix_to_datetime(unix_timestamp)

    # Calculate the difference in seconds
    time_diff_seconds = (current_utc_time - target_datetime).total_seconds()

    # Check if the difference is within the tolerance
    return abs(time_diff_seconds) <= tolerance_seconds


def create_table(conn, create_table_sql):
    """Create a table from the create_table_sql statement."""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Exception as e:
        print(e)


def create_connection(db_file):
    """Create a database connection to a SQLite database."""
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        return conn
    except Exception as e:
        print(e)
        return None

database = 'rag_response_logging.db'



def process_whatsapp_message(body, req_time):

    sql_create_rag_responses_table = """CREATE TABLE IF NOT EXISTS RAG_timed_logs (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    PhoneNumber TEXT,
    UserQuery TEXT,
    BotResponse TEXT,
    CreatedDate TEXT,
    CreatedTime TEXT,
    "Latency(s)" INTEGER
    ); """

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_rag_responses_table)
        print("Table created successfully.")
    else:
        print("Error! Cannot create the database connection.")

    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
    display_number = body["entry"][0]["changes"][0]["value"]["metadata"]["display_phone_number"]

    print(f"BODY: {body}")
    if wa_id not in whatsapp_recepient_question_set.keys():
        whatsapp_recepient_question_set[wa_id] = \
            {"message_history": [{"role": "system",
                                     "content": "You are an helpful assistant that answers all general queries related to"
                                             " Meghalaya Public Services Delivery Commision using your knowledge base. "
                                             "Do not answer queries that are not related to Meghalaya Public Services Delivery Commision."}],
             "previous_messages": []}
    elif len(whatsapp_recepient_question_set[wa_id]["message_history"]) > 20:
        whatsapp_recepient_question_set[wa_id].clear()
        whatsapp_recepient_question_set[wa_id] = \
            {"message_history": [{"role": "system",
                                     "content": "You are an helpful assistant that answers all general queries related to"
                                              " Meghalaya Public Services Delivery Commision using your knowledge base. "
                                             "Do not answer queries that are not related to Meghalaya Public Services Delivery Commision."}],
             "previous_messages": []}

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    try:
        if message["type"] == "text":
            print("*1")
            message_body = message["text"]["body"]
            print(
                f"Display number: {display_number}, Message body: {message_body} and message from {body['entry'][0]['changes'][0]['value']['contacts']}")

            if display_number == '919811294652':
                print("*2")
                whatsapp_recepient_question_set[wa_id]["message_history"].append({"role": "user", "content": message_body})

                if is_general_question(message_body) == "True":
                    print("*3")
                
                    translated_general_msg = translate(message_body, general_response)

                    translated_msg_parts = translated_general_msg.split("\n")
                    msg_to_be_sent = translated_msg_parts[-1].split(":")[-1].strip()

                    data = get_text_message_input(wa_id, msg_to_be_sent)
                    send_message(data)
                    whatsapp_recepient_question_set[wa_id]["message_history"].append({"role": "system", "content": general_response})
                else: 
                    print("*4")

                    # message_type = check_message_type(message_body)
                    message_type = "t"
                    if not message_type == 'greeting': #SQL or Unstructured query
                        print("*5")
                        # message_to_be_sent = random.choice(preprocess_responses)
                        # translated_msg = translate(whatsapp_recepient_question_set[wa_id]["message_history"][-1]['content'],
                        #                            message_to_be_sent)

                        # translated_msg_parts = translated_msg.split("\n")
                        # msg_to_be_sent = translated_msg_parts[-1].split(":")[-1].strip()

                        # pre_response = get_text_message_input(wa_id, msg_to_be_sent)
                        # send_message(pre_response)
                        # whatsapp_recepient_question_set[wa_id]["message_history"].append(
                        #     {"role": "system", "content": pre_response})

                        # refined_query = refine_query(message_body, whatsapp_recepient_question_set[wa_id]["message_history"])
                        # whatsapp_recepient_question_set[wa_id]["previous_messages"].append(refined_query)
                        # response, updated_message_history, resp_time = generate_response(wa_id, refined_query, message_type,
                        #                                                       whatsapp_recepient_question_set[wa_id]["message_history"], "wp")

                    
                        response, updated_message_history, resp_time = generate_response(wa_id, message_body, message_type,
                                                                              whatsapp_recepient_question_set[wa_id]["message_history"], "wp")
                        # insert_rag_response(conn, wa_id, message_body, response, "Whatsapp", req_time, resp_time)
                    else:
                        print("*6")
                        response, placeholder, resp_time = generate_response(wa_id, message_body, message_type,
                                                                              whatsapp_recepient_question_set[wa_id]["message_history"], "wp")
                    insert_rag_response(conn, wa_id, message_body, response, "Whatsapp", req_time, resp_time)
                    data = get_text_message_input(wa_id, response)
                    print(f"Output for app.py: {response}")
                    send_message(data)
                    if not message_type == "greeting":
                        for message in updated_message_history:
                            whatsapp_recepient_question_set[wa_id]["message_history"].append(message)
                
            else:
                print("*8")
                print("Request from Phone number is invalid...")
        else:
            print("*9")
            no_text_response = ("I am here to help you with any form of text queries related to Meghalaya State Public Services Delivery Commission (MSPSDC), "
                                "please ask me anything in that context and I'd be happy to assist you!")
            translated_reponse = no_text_response
            # translated_reponse = translate(whatsapp_recepient_question_set[wa_id]["message_history"][-1]['content'], no_text_response)

            translated_msg_parts = translated_reponse.split("\n")
            msg_to_be_sent = translated_msg_parts[-1].split(":")[-1].strip()
            send_response = get_text_message_input(wa_id, msg_to_be_sent)
            send_message(send_response)
            
    except Exception as e:
        send_response = get_text_message_input(wa_id, "I'm undergoing some maintainence tasks, please contact later...")
        send_message(send_response)
        print("he1")
        print(f"ERROR: {e}")





def insert_rag_response(connection, user_id, user_query, rag_response, channel, req_time, resp_time):
    print("INSERTING RAG RESPONSE***********")
    """Insert a new row into the rag_responses table with the current UTC datetime."""
    if connection is not None:
        try:

            # Convert time strings to datetime objects
            req_time = datetime.datetime.strptime(req_time, "%H:%M:%S.%f")
            resp_time = datetime.datetime.strptime(resp_time, "%H:%M:%S.%f")

            # Calculate the difference (timedelta)
            time_diff = resp_time - req_time

            total_seconds = time_diff.total_seconds()

            # Current UTC datetime
            now = datetime.datetime.now()
            today_str = now.strftime("%d-%m-%Y")
            current_time_str = now.strftime("%H:%M:%S")

            # formatted_date = created_datetime.strftime("%d-%m-%Y")


            # SQL query to insert data
            query = """
            INSERT INTO RAG_timed_logs (PhoneNumber, UserQuery, BotResponse, CreatedDate, CreatedTime, "Latency(s)")
            VALUES (?, ?, ?, ?, ?, ?)
            """

            # Data tuple
            data = (user_id, user_query, rag_response, today_str, current_time_str, total_seconds)

            # Execute the query
            cursor = connection.cursor()
            cursor.execute(query, data)
            connection.commit()
            print("!"*50)
            print(f"Record inserted successfully into rag_responses table, ID: {cursor.lastrowid}")
            print("!"*50)

        
        except Exception as e:
            print("!"*50)
            print(f"Error while connecting to SQLite: {e}")
            print("!"*50)



def send_response_to_slack(channel_id, message, user_id):
    # This function would use the Slack API's `chat.postMessage` method to send a response back to the user
    # You need to use your bot's OAuth token to authenticate the request
    import requests
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        'Authorization': '',
        'Content-Type': 'application/json'
    }
    data = {
        'channel': channel_id,
        'text': message
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Message successfully sent to {user_id} in channel {channel_id}")
    else:
        print(f"Failed to send message to {user_id} in channel {channel_id}, error: {response.text}")


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
            body.get("object")
            and body.get("entry")
            and body["entry"][0].get("changes")
            and body["entry"][0]["changes"][0].get("value")
            and body["entry"][0]["changes"][0]["value"].get("messages")
            and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )

