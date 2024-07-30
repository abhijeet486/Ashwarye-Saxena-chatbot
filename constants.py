table_schema = {
    "Notifications": {
        "description": "Stores information about notifications issued by various departments. Information consist of Notification ID, Notification Number, Department, Notification Date, and Notification URL.",
        "column_definitions": {
            "Notification_ID": "Unique identifier for each notification (INTEGER, PRIMARY KEY)",
            "Notification_Number": "Notification number (TEXT, NOT NULL)",
            "Department": "Department or office issuing the notification (TEXT, NOT NULL)",
            "Notification_Date": "Date of the notification (DATE)",
            "Notification_URL": "URL of the notification (TEXT, UNIQUE)"
        }
    }
}

