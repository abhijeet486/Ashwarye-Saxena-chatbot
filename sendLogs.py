from apscheduler.schedulers.blocking import BlockingScheduler
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sqlite3
from datetime import datetime, timedelta
import os
from openpyxl import Workbook
from openpyxl.styles import Alignment


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
        recipients = ['abhit.rana@ihub-anubhuti-iiitd.org']
        cc_recipients = ['rajeev.pandey@ihub-anubhuti-iiitd.org', 'rajeev.goel@ihub-anubhuti-iiitd.org', 'ashwarye.saxena@ihub-anubhuti-iiitd.org', 'hitesh.bhandari@ihub-anubhuti-iiitd.org', 'abhijeet.singh@ihub-anubhuti-iiitd.org', 'aman.sharma@ihub-anubhuti-iiitd.org']
        msg['To'] = ', '.join(recipients)
        msg['Cc'] = ', '.join(cc_recipients)
        msg['Subject'] = 'MSPSDC Chatbot Usage Logs'

        # Get today's date
        now = datetime.now()

        # Get the previous day's date
        yesterday = now - timedelta(1)

        yesterday_date = yesterday.strftime("%d-%m-%Y")  # Ensure correct format for SQL query

        # print(yesterday_date)

        # Connect to SQLite database
        conn = sqlite3.connect('rag_response_logging.db')
        cur = conn.cursor()

        # Query records for the previous day
        cur.execute("SELECT * FROM RAG_timed_logs WHERE CreatedDate >= ?", (yesterday_date,))

        records = cur.fetchall()

        # print(records)

        if not records:
            # No records found for today
            body = "This is an automated email. Please do not respond. \n\nNo usage logs for today."
            msg.attach(MIMEText(body, 'plain'))
        else:
            # Records found, proceed with attaching Excel file
            body = "This is an automated email. Please do not respond. \n\nAttached are the usage logs for the Meghalaya State Public Services Delivery Commission (MSPSDC) Chatbot"
            msg.attach(MIMEText(body, 'plain'))

            # Convert records to Excel
            excel_filename = "MSPSDC.Chatbot.Usage." + yesterday_date + ".xlsx"
            output_dir = "./RAG_logs"
            os.makedirs(output_dir, exist_ok=True)
            excel_filepath = os.path.join(output_dir, excel_filename)

            wb = Workbook()
            ws = wb.active
            ws.title = "Usage Logs"

            # Write headers
            headers = [i[0] for i in cur.description]
            ws.append(headers)

            for record in records:
                ws.append(record)

            # max_width = 60  # Set the maximum width limit for columns
            # for col in ws.columns:
            #     max_length = 0
            #     column = col[0].column_letter  # Get the column name
            #     for cell in col:
            #         cell.alignment = Alignment(wrap_text=True)
            #         if len(str(cell.value)) > max_length:
            #             max_length = len(cell.value)
            #     adjusted_width = min((max_length+2), max_width)
            #     ws.column_dimensions[column].width = adjusted_width

            for col in ws.columns:
                column = col[0].column_letter  # Get the column name (letter)
                # print(column)
                if column == 'C':  # Second column
                    ws.column_dimensions[column].width = 40
                    for cell in col:
                        cell.alignment = Alignment(wrap_text=True)
                elif column == 'D':  # Third column
                    ws.column_dimensions[column].width = 80
                    for cell in col:
                        cell.alignment = Alignment(wrap_text=True)
                else:
                    max_length = 0
                    for cell in col:
                        cell.alignment = Alignment(wrap_text=True)
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    adjusted_width = min((max_length+2), 60)
                    ws.column_dimensions[column].width = adjusted_width

            # Save the Excel file
            wb.save(excel_filepath)

            # Attach Excel file
            with open(excel_filepath, "rb") as attachment:
                part = MIMEBase('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {excel_filename}")
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
    # APScheduler
    scheduler = BlockingScheduler()

    # Schedule the email sending task to run daily at 12:00 AM 
    scheduler.add_job(send_email, 'cron', hour=0, minute=0, id='midnight_job')

    # scheduler.add_job(send_email, 'interval', minutes=1, id='minute_job')

    # scheduler.add_job(send_email, 'interval', seconds=10, id='interval_job')

    print("Scheduler started. Waiting for scheduled emails...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler terminated.")
