# CRUD REST API (Flask + MySQL)

A simple REST API for managing "people" records, built with Flask and
PyMySQL. Every response is JSON.

## Technologies used

- Python
- Flask
- PyMySQL
- MySQL


## Create the database

Run this in MySQL (Workbench or the command line):

```sql
CREATE DATABASE crud_api;

USE crud_api;

CREATE TABLE people (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    age INT NOT NULL
);
```

## Configure your password

Open `database.py` and replace `YOUR_PASSWORD` with your own MySQL password.

## Run the API

```bash
python app.py
```

The API runs at `http://127.0.0.1:5000`.

## Endpoints

| Method | URL              | Description         |
|--------|------------------|----------------------|
| GET    | /people          | List all people      |
| GET    | /people/<id>     | Get one person       |
| POST   | /people          | Create a new person  |
| PUT    | /people/<id>     | Update a person      |
| DELETE | /people/<id>     | Delete a person      |

## Example request/response

**POST /people**

Request body:
```json
{
    "name": "Ahmed",
    "email": "ahmed@gmail.com",
    "age": 21
}
```

Response (201 Created):
```json
{
    "message": "Person created successfully",
    "id": 1
}
```

## HTTP status codes used

| Status | Meaning               | Example                          |
|--------|-----------------------|-----------------------------------|
| 200    | Successful request     | GET /people/1                    |
| 201    | Resource created       | POST /people                     |
| 400    | Invalid request/input  | Missing name, duplicate email    |
| 404    | Resource not found     | GET /people/999                  |
| 500    | Server error           | Unexpected server problem        |
