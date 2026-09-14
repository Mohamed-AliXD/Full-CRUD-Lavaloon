from flask import Flask, request, jsonify

from database import get_connection

app = Flask(__name__)

def validate_person_data(data):
    if not data:
        return "Request body is required"

    if "name" not in data or str(data["name"]).strip() == "":
        return "Name is required"

    if "email" not in data or str(data["email"]).strip() == "":
        return "Email is required"

    if "age" not in data:
        return "Age is required"

    try:
        age = int(data["age"])
    except (ValueError, TypeError):
        return "Age must be an integer"

    if age <= 0 or age > 150:
        return "Age must be a reasonable positive number"

    return None



@app.route("/people", methods=["GET"])
def get_people():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM people")
    people = cursor.fetchall()
    cursor.close()
    connection.close()

    return jsonify({"people": people}), 200



@app.route("/people/<int:person_id>", methods=["GET"])
def get_person(person_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM people WHERE id = %s", (person_id,))
    person = cursor.fetchone()
    cursor.close()
    connection.close()

    if person is None:
        return jsonify({"error": "Person not found"}), 404

    return jsonify(person), 200



@app.route("/people", methods=["POST"])
def create_person():
    data = request.get_json(silent=True)

    error_message = validate_person_data(data)
    if error_message is not None:
        return jsonify({"error": error_message}), 400

    name = str(data["name"]).strip()
    email = str(data["email"]).strip()
    age = int(data["age"])

    connection = get_connection()
    cursor = connection.cursor()

   
    cursor.execute("SELECT id FROM people WHERE email = %s", (email,))
    existing_person = cursor.fetchone()
    if existing_person is not None:
        cursor.close()
        connection.close()
        return jsonify({"error": "Email already exists"}), 400

    cursor.execute(
        "INSERT INTO people (name, email, age) VALUES (%s, %s, %s)",
        (name, email, age)
    )
    connection.commit()
    new_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Person created successfully",
        "id": new_id
    }), 201



@app.route("/people/<int:person_id>", methods=["PUT"])
def update_person(person_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM people WHERE id = %s", (person_id,))
    existing_person = cursor.fetchone()
    if existing_person is None:
        cursor.close()
        connection.close()
        return jsonify({"error": "Person not found"}), 404

    data = request.get_json(silent=True)
    error_message = validate_person_data(data)
    if error_message is not None:
        cursor.close()
        connection.close()
        return jsonify({"error": error_message}), 400

    name = str(data["name"]).strip()
    email = str(data["email"]).strip()
    age = int(data["age"])
    cursor.execute(
        "SELECT id FROM people WHERE email = %s AND id != %s",
        (email, person_id)
    )
    email_owner = cursor.fetchone()
    if email_owner is not None:
        cursor.close()
        connection.close()
        return jsonify({"error": "Email already exists"}), 400

    cursor.execute(
        "UPDATE people SET name = %s, email = %s, age = %s WHERE id = %s",
        (name, email, age, person_id)
    )
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Person updated successfully"}), 200


@app.route("/people/<int:person_id>", methods=["DELETE"])
def delete_person(person_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM people WHERE id = %s", (person_id,))
    existing_person = cursor.fetchone()
    if existing_person is None:
        cursor.close()
        connection.close()
        return jsonify({"error": "Person not found"}), 404

    cursor.execute("DELETE FROM people WHERE id = %s", (person_id,))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Person deleted successfully"}), 200



@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(400)
def handle_bad_request(error):
    return jsonify({"error": "Bad request"}), 400


@app.errorhandler(500)
def handle_server_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True)
