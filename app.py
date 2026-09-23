from flask import Flask, render_template, request, session, redirect, url_for
import math
import os
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    return connection


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/first-aid")
def first_aid():
    language = request.args.get("lang", "en")

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM first_aid_topics")

    topics = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "first_aid.html",
        topics=topics,
        language=language
    )

@app.route("/first-aid/<int:topic_id>")
def first_aid_detail(topic_id):
    language = request.args.get("lang", "en")

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM first_aid_topics WHERE id = %s",
        (topic_id,)
    )

    topic = cursor.fetchone()

    cursor.close()
    connection.close()

    if topic is None:
        return "First-aid topic not found", 404

    return render_template(
        "first_aid_detail.html",
        topic=topic,
        language=language
    )

@app.route("/hospitals")
def hospitals():
    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM hospitals")

    hospitals = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "hospitals.html",
        hospitals=hospitals
    )

@app.route("/nearby-hospitals")
def nearby_hospitals():
    latitude = float(request.args.get("latitude"))
    longitude = float(request.args.get("longitude"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM hospitals")
    hospitals = cursor.fetchall()

    cursor.close()
    connection.close()

    nearby = []

    for hospital in hospitals:
        hospital_lat = float(hospital["latitude"])
        hospital_lon = float(hospital["longitude"])

        lat_difference = math.radians(hospital_lat - latitude)
        lon_difference = math.radians(hospital_lon - longitude)

        a = (
            math.sin(lat_difference / 2) ** 2
            + math.cos(math.radians(latitude))
            * math.cos(math.radians(hospital_lat))
            * math.sin(lon_difference / 2) ** 2
        )

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = 6371 * c

        hospital["distance"] = round(distance, 2)

        nearby.append(hospital)

    nearby.sort(key=lambda hospital: hospital["distance"])

    return render_template(
        "nearby_hospitals.html",
        hospitals=nearby,
        latitude=latitude,
        longitude=longitude
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    error = None

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM admins WHERE username = %s",
            (username,)
        )

        admin = cursor.fetchone()

        cursor.close()
        connection.close()

        if admin and check_password_hash(
            admin["password_hash"],
            password
        ):
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]

            return redirect(url_for("admin_dashboard"))

        error = "Invalid username or password."

    return render_template(
        "admin_login.html",
        error=error
    )


@app.route("/admin/dashboard")
def admin_dashboard():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM hospitals")
    hospital_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM first_aid_topics")
    first_aid_count = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return render_template(
        "admin_dashboard.html",
        hospital_count=hospital_count,
        first_aid_count=first_aid_count
    )

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(url_for("admin_login"))

@app.route("/admin/hospitals")
def admin_hospitals():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM hospitals ORDER BY id DESC")

    hospitals = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin_hospitals.html",
        hospitals=hospitals
    )


@app.route("/admin/hospitals/add", methods=["GET", "POST"])
def add_hospital():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":

        name = request.form["name"]
        address = request.form["address"]
        latitude = request.form["latitude"]
        longitude = request.form["longitude"]
        phone = request.form["phone"]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO hospitals
            (name, address, latitude, longitude, phone)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, address, latitude, longitude, phone)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("admin_hospitals"))

    return render_template("add_hospital.html")


@app.route("/admin/hospitals/edit/<int:hospital_id>", methods=["GET", "POST"])
def edit_hospital(hospital_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form["name"]
        address = request.form["address"]
        latitude = request.form["latitude"]
        longitude = request.form["longitude"]
        phone = request.form["phone"]

        cursor.execute(
            """
            UPDATE hospitals
            SET name = %s,
                address = %s,
                latitude = %s,
                longitude = %s,
                phone = %s
            WHERE id = %s
            """,
            (name, address, latitude, longitude, phone, hospital_id)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("admin_hospitals"))

    cursor.execute(
        "SELECT * FROM hospitals WHERE id = %s",
        (hospital_id,)
    )

    hospital = cursor.fetchone()

    cursor.close()
    connection.close()

    if hospital is None:
        return "Hospital not found", 404

    return render_template(
        "edit_hospital.html",
        hospital=hospital
    )


@app.route("/admin/hospitals/delete/<int:hospital_id>", methods=["POST"])
def delete_hospital(hospital_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM hospitals WHERE id = %s",
        (hospital_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("admin_hospitals"))


@app.route("/admin/first-aid")
def admin_first_aid():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM first_aid_topics ORDER BY id DESC"
    )

    topics = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin_first_aid.html",
        topics=topics
    )

@app.route("/admin/first-aid/add", methods=["GET", "POST"])
def add_first_aid():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":

        title_en = request.form["title_en"]
        title_ta = request.form["title_ta"]

        description_en = request.form["description_en"]
        description_ta = request.form["description_ta"]

        steps_en = request.form["steps_en"]
        steps_ta = request.form["steps_ta"]

        warning_en = request.form["warning_en"]
        warning_ta = request.form["warning_ta"]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO first_aid_topics
            (
                title_en,
                title_ta,
                description_en,
                description_ta,
                steps_en,
                steps_ta,
                warning_en,
                warning_ta
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                title_en,
                title_ta,
                description_en,
                description_ta,
                steps_en,
                steps_ta,
                warning_en,
                warning_ta
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("admin_first_aid"))

    return render_template("add_first_aid.html")


@app.route("/admin/first-aid/edit/<int:topic_id>", methods=["GET", "POST"])
def edit_first_aid(topic_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        title_en = request.form["title_en"]
        title_ta = request.form["title_ta"]

        description_en = request.form["description_en"]
        description_ta = request.form["description_ta"]

        steps_en = request.form["steps_en"]
        steps_ta = request.form["steps_ta"]

        warning_en = request.form["warning_en"]
        warning_ta = request.form["warning_ta"]

        cursor.execute(
            """
            UPDATE first_aid_topics
            SET title_en = %s,
                title_ta = %s,
                description_en = %s,
                description_ta = %s,
                steps_en = %s,
                steps_ta = %s,
                warning_en = %s,
                warning_ta = %s
            WHERE id = %s
            """,
            (
                title_en,
                title_ta,
                description_en,
                description_ta,
                steps_en,
                steps_ta,
                warning_en,
                warning_ta,
                topic_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("admin_first_aid"))

    cursor.execute(
        "SELECT * FROM first_aid_topics WHERE id = %s",
        (topic_id,)
    )

    topic = cursor.fetchone()

    cursor.close()
    connection.close()

    if topic is None:
        return "First-aid topic not found", 404

    return render_template(
        "edit_first_aid.html",
        topic=topic
    )


@app.route("/admin/first-aid/delete/<int:topic_id>", methods=["POST"])
def delete_first_aid(topic_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM first_aid_topics WHERE id = %s",
        (topic_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("admin_first_aid"))

if __name__ == "__main__":
    app.run(debug=True)
