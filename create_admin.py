import mysql.connector
from werkzeug.security import generate_password_hash

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Arnesh@2003",
    database="rescuereach",
    charset="utf8mb4"
)

cursor = connection.cursor()

username = "admin"
password = "Admin@123"

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