import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Arnesh@2003",
    database="rescuereach",
    charset="utf8mb4"
)

cursor = connection.cursor()

sql = """
UPDATE first_aid_topics
SET
    title_ta = %s,
    description_ta = %s,
    steps_ta = %s,
    warning_ta = %s
WHERE id = 4
"""

values = (
    "வெட்டுக்காயம்",
    "சிறிய வெட்டுக்காயத்திற்கு அடிப்படை முதலுதவி வழிகாட்டுதல்.",
    "உங்கள் கைகளை சுத்தமாக கழுவுங்கள். வெட்டுக்காயத்தை சுத்தமான தண்ணீரால் மெதுவாக சுத்தம் செய்யுங்கள். இரத்தப்போக்கை கட்டுப்படுத்த சுத்தமான துணி அல்லது காஸால் மெதுவாக அழுத்தம் கொடுக்கவும். காயத்தை சுத்தமான கட்டுடன் மூடவும்.",
    "இரத்தப்போக்கு அதிகமாக இருந்தால் அல்லது நிற்கவில்லை என்றால், அல்லது காயம் ஆழமாக இருந்தால், உடனடியாக மருத்துவ உதவியை நாடுங்கள்."
)

cursor.execute(sql, values)

connection.commit()

cursor.close()
connection.close()

print("Cuts Tamil data updated successfully!")