"""
app.py

A simple Flask REST API for managing "people" records in MySQL.

Endpoints:
    GET    /people        -> list all people
    GET    /people/<id>   -> get one person
    POST   /people        -> create a new person
    PUT    /people/<id>   -> update an existing person
    DELETE /people/<id>   -> delete a person

All responses are JSON. Errors are handled in one centralized place
using Flask's errorhandler mechanism, instead of try/except in every route.
"""

from flask import Flask, request, jsonify

from database import get_connection

app = Flask(__name__)


# ---------------------------------------------------------------------
# Small helper function used by POST and PUT to check the submitted data.
# Having this in one place means we don't repeat the same checks twice.
# ---------------------------------------------------------------------
def validate_person_data(data):
    """
    Check that the submitted person data is valid.
    Returns an error message (string) if something is wrong,
    or None if everything is fine.
    """
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


# ---------------------------------------------------------------------
# GET all people
# ---------------------------------------------------------------------
@app.route("/people", methods=["GET"])
def get_people():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM people")
    people = cursor.fetchall()
    cursor.close()
    connection.close()

    # If there are no records, "people" will just be an empty list.
    # That is normal, not an error.
    return jsonify({"people": people}), 200


# ---------------------------------------------------------------------
# GET one person by id
# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
# POST - create a new person
# ---------------------------------------------------------------------
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

    # Check if the email is already used by someone else.
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


# ---------------------------------------------------------------------
# PUT - update an existing person
# ---------------------------------------------------------------------
@app.route("/people/<int:person_id>", methods=["PUT"])
def update_person(person_id):
    connection = get_connection()
    cursor = connection.cursor()

    # First, check the person actually exists.
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

    # Make sure the new email isn't already used by a DIFFERENT person.
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


# ---------------------------------------------------------------------
# DELETE - remove a person
# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
# Centralized error handlers.
# These catch errors for the WHOLE app, so we don't need
# try/except blocks inside every single route above.
# ---------------------------------------------------------------------
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
