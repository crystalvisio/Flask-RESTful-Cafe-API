# Import necessary Libraries
import os
import random
import logging
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, render_template, request, abort

# Load environment variables from .env file
load_dotenv()
SECRET_KEY = os.getenv("API_KEY")

app = Flask(__name__)

# Initialize the logger
logging.basicConfig(filename='app.log', level=logging.INFO)

# Initialize the rate limiter
limiter = Limiter(app, key_func =get_remote_address)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///instance/cafes.db"
db = SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    # Define the fields for the Cafe table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    # Convert the data record to a dictionary
    def to_dict(self):
        
        # USING DICTIONARY COMPREHENSION
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

        """
        # WITHOUT DICTIONARY COMPREHENSION
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            #Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary
        """


# Create the database
with app.create_contect():
    db.create_all()


# Custom error handler for 404 errors
@app.errorhandler(404)
def resource_not_found(e):
    # Return a JSON response with the error message and a 404 status code
    return jsonify(error=str(e)), 404


# Custom error handler for 400 errors
@app.errorhandler(400)
def invalid_request(e):
    # Return a JSON response with the error message and a 400 status code
    return jsonify(error=str(e)), 400


# Route to homepage
@app.route("/")
def home():
    # render the homepage
    return render_template("index.html")


# Route to all the cafe
@app.route("/all", methods = ["GET"])
@limiter.limit("100/day") # Limit request to 100 per day
def all_cafe():
    # Fetch all cafes from the database and return them as JSON
    result = db.session.execute(db.select(Cafe)).scalars().all()
    all_cafes = [cafes.to_dict() for cafes in result]
    return jsonify(cafe = all_cafes)


# Route to getting a random cafe
@app.route("/random", methods = ["GET"])
def random_cafe():
    result = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe = (random.choice(result))
    # using the create function that creates dict
    return jsonify(cafe = random_cafe.to_dict())

    """
    # Can use this method or just use a function to create a dictionary before... refer to class Cafe
    return jsonify(cafe= {
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "has_sockets": random_cafe.has_sockets,
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price
    })
    """

# Route to searching specific cafe
@app.route("/search", methods = ["GET"])
def search_cafe():
    # Fetch cafes from the database based on a location query and return them as JSON
    query_loc = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_loc))
    all_cafes = result.scalars().all()

    if all_cafes:
        return jsonify(cafe = [cafes.to_dict() for cafes in all_cafes])
    
    else:
        return jsonify(error= {"Not Found": "Sorry, we don't have a cafe at that location."}), 404


@app.route("/add", methods = ["POST"])
def add_cafe():
    new_cafe_data = request.form
    # Check if all required fields are present in the request data
    if not all(field in new_cafe_data for field in Cafe.required_fields):
        # If not, abort the request with a 400 error and a custom error message
        abort(400, description="Missing required field(s)")

    # Add a new cafe to the database
    new_cafe = Cafe(
        name = request.form.get("name"),
        map_url = request.form.get("map_url"),
        img_url = request.form.get("img_url"),
        location = request.form.get("location"),
        has_sockets = request.form.get("has_sockets") == "True", 
        has_toilet = request.form.get("has_toilet") == "True",
        has_wifi = request.form.get("has_wifi") == "True",
        can_take_calls = request.form.get("can_take_calls") == "True",
        seats = request.form.get("seats"),
        coffee_price = request.form.get("coffee_price")
    )

    db.session.add(new_cafe) 
    db.session.commit()

    return jsonify(response = {"Success": "Succesfully added the new cafe."})  


@app.route("/update/<int:cafe_id>", methods = ["PATCH"])
def update_price(cafe_id):
    # Update the price of a specific cafe
    price_to_update = db.session.get(Cafe, cafe_id)
    new_price = request.form.get("new_price")
    # Check if the new_price field is present in the request data
    if not new_price:
        # If not, abort the request with a 400 error and a custom error message
        abort(400, description="Missing new_price field")

    if price_to_update:
        price_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response = {"Success": "Succesfully updated the price."})

    else:
        return jsonify(error = {"Not Found": "Sorry a cafe with that id was not found in the database."})


@app.route("/delete/<int:cafe_id>", methods = ["DELETE"])
def delete(cafe_id):
    # Delete a specific cafe from the database
    cafe_to_delete = db.session.get(Cafe, cafe_id)
    api_key = request.args.get("api_key")
    # Check if the api_key field is present in the request data
    if not api_key:
        # If not, abort the request with a 400 error and a custom error message
        abort(400, description="Missing api_key field")

    if not cafe_to_delete:
        return jsonify(error = {"Not Found": "Sorry a cafe with that id was not found in the database."})

    if api_key != SECRET_KEY:
        return jsonify(error = {"Invalid": "The entered API key is not valid"})

    db.session.delete(cafe_to_delete)
    db.session.commit()
    return jsonify(response = {"Success": "Successfully deleted the cafe."})


if __name__ == "__main__":
    app.run(debug=False)
