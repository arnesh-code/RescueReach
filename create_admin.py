import os
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset="utf8mb4"
)

cursor = connection.cursor()

username = input("Enter admin username: ")
password = input("Enter admin password: ")

password_hash = generate_password_hash(password)

sql = """
INSERT INTO admins (username, password_hash)
VALUES (%s, %s)
"""

cursor.execute(sql, (username, password_hash))

connection.commit()

cursor.close()
connection.close()

print("Admin account created successfully!")