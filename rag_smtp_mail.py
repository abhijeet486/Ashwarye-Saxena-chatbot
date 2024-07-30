import smtplib
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sqlite3
from datetime import datetime
import os


def send_email():
    # SMTP server configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465  # Since you're using port 465, which typically requires SSL/TLS from the start
    smtp_username = 'chatbot.feedback@ihub-anubhuti-iiitd.org'
    smtp_password = 'tmfp ccwj rpeo ccmi'

    # Connect to SMTP server
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)

    try:
        # Login to the SMTP server
        server.login(smtp_username, smtp_password)

        # Compose email
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        recipients = ['vishva.rana@softmaxai.com', 'ceo@ihub-anubhuti-iiitd.org', 'cto@ihub-anubhuti-iiitd.org', 'rajeev.goel@ihub-anubhuti-iiitd.org']
        msg['To'] = ', '.join(recipients) 
        msg['Subject'] = 'MoRD PMGSY Chatbot Usage Logs'

        body = "This is an automated email. Please do not respond. Attached are the usage logs for the MoRD PMGSY Chatbot"
        msg.attach(MIMEText(body, 'plain'))

        # Get today's date
        today = datetime.now().date()

        # Connect to SQLite database
        conn = sqlite3.connect('/home/ubuntu/python-whatsapp-bot-0404/rag_response_logging.db')
        cur = conn.cursor()

        # Query records for today
        cur.execute("SELECT * FROM RAG_timed_logs WHERE CreatedDatetime >= ?", (today,))
        records = cur.fetchall()

        # Convert records to CSV
        csv_filename = "MoRD.Chatbot.Usage." + today.strftime("%d-%m-%Y") + ".csv"
        csv_filepath = os.path.join(output_dir, csv_filename)
        with open(csv_filepath, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([i[0] for i in cur.description])  # Write headers
            csv_writer.writerows(records)

        # Attach CSV file
        with open(csv_filepath, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {csv_filename}")
            msg.attach(part)

        # Send email
        server.send_message(msg)
        print("Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")

    finally:
        # Close the connection
        server.quit()


if __name__ == "__main__":
    output_dir = "./RAG_logs"
    os.makedirs(output_dir, exist_ok=True)
    send_email()