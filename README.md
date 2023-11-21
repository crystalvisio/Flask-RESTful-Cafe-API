# Flask-RESTful-Cafe-API

## Description
This repository contains a practice code for a RESTful API using Flask. The API is designed for a hypothetical cafe, allowing users to perform CRUD (Create, Read, Update, Delete) operations on the cafe data.

## Features
- **Flask**: A lightweight WSGI web application framework.
- **Flask-SQLAlchemy**: An extension for Flask that adds support for SQLAlchemy to your application.
- **Flask-Limiter**: An extension for Flask that provides rate limiting features.
- **dotenv**: A zero-dependency module that loads environment variables from a `.env` file into `process.env`.

## Endpoints
- **GET /all**: Fetch all cafes from the database.
- **GET /random**: Fetch a random cafe from the database.
- **GET /search**: Fetch cafes from the database based on a location query.
- **POST /add**: Add a new cafe to the database.
- **PATCH /update/<int:cafe_id>**: Update the price of a specific cafe.
- **DELETE /delete/<int:cafe_id>**: Delete a specific cafe from the database.

## Installation
1. Clone this repository.
2. Install the dependencies using pip:
    ```
    pip install -r requirements.txt
    ```
3. Run the application:
    ```
    python main.py
    ```

## Note
This is a practice project and is not intended for production use. The API key is stored in an environment variable for security purposes. Please replace it with your own secret key.

## License
This project is licensed under the terms of the MIT license. For more information, please refer to the LICENSE file. 

## Contributing
Contributing is welcome.
