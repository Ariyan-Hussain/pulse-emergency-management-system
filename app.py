from flask import Flask, render_template, request
from database import get_connection

app = Flask(__name__)


# Dashboard Route
@app.route("/")
def home():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    # Total patients
    cursor.execute("SELECT COUNT(*) AS total FROM patients")
    patient_count = cursor.fetchall()[0]["total"]

    # Total hospitals
    cursor.execute("SELECT COUNT(*) AS total FROM hospitals")
    hospital_count = cursor.fetchall()[0]["total"]

    # Total emergency cases
    cursor.execute("SELECT COUNT(*) AS total FROM emergencies")
    emergency_count = cursor.fetchall()[0]["total"]

    # Total available beds
    cursor.execute("""
        SELECT COALESCE(SUM(available_beds), 0) AS total
        FROM hospitals
    """)
    available_beds = cursor.fetchall()[0]["total"]

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        patient_count=patient_count,
        hospital_count=hospital_count,
        emergency_count=emergency_count,
        available_beds=available_beds
    )
# Patient Route
@app.route("/patients", methods=["GET", "POST"])
def patients():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        blood_group = request.form["blood_group"]
        emergency_type = request.form["emergency_type"]
        priority = request.form["priority"]

        query = """
        INSERT INTO patients
        (name, age, gender, phone, blood_group, emergency_type, priority)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            name,
            age,
            gender,
            phone,
            blood_group,
            emergency_type,
            priority
        )

        cursor.execute(query, values)
        connection.commit()

    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    patient_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "patients.html",
        patients=patient_list
    )


# Emergency Management Route
@app.route("/emergency", methods=["GET", "POST"])
def emergency():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        patient_id = request.form["patient_id"]
        hospital_id = request.form["hospital_id"]
        emergency_type = request.form["emergency_type"]
        severity = request.form["severity"]
        status = request.form["status"]

        query = """
        INSERT INTO emergencies
        (patient_id, hospital_id, emergency_type, severity, status)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            patient_id,
            hospital_id,
            emergency_type,
            severity,
            status
        )

        cursor.execute(query, values)
        connection.commit()

    # Get patients
    cursor.execute(
        "SELECT id, name FROM patients ORDER BY name"
    )

    patient_list = cursor.fetchall()

    # Get hospitals
    cursor.execute(
        "SELECT id, name FROM hospitals ORDER BY name"
    )

    hospital_list = cursor.fetchall()

    # Get emergency cases
    cursor.execute("""
        SELECT
            emergencies.id,
            patients.name AS patient_name,
            hospitals.name AS hospital_name,
            emergencies.emergency_type,
            emergencies.severity,
            emergencies.status
        FROM emergencies
        JOIN patients
            ON emergencies.patient_id = patients.id
        JOIN hospitals
            ON emergencies.hospital_id = hospitals.id
        ORDER BY emergencies.id DESC
    """)

    emergency_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "emergency.html",
        patients=patient_list,
        hospitals=hospital_list,
        emergencies=emergency_list
    )
    
# Hospital Management Route
@app.route("/hospitals")
def hospitals():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM hospitals
        ORDER BY name
    """)

    hospital_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "hospitals.html",
        hospitals=hospital_list
    )
# Bed Management Route
@app.route("/beds")
def beds():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            name,
            total_beds,
            available_beds
        FROM hospitals
        ORDER BY name
    """)

    hospital_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "beds.html",
        hospitals=hospital_list
    )

# This MUST be at the very bottom
if __name__ == "__main__":
    app.run(debug=True)