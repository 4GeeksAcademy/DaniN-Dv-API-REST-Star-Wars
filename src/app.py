"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorites
#from models import Person
from moks.people import people
from moks.planets import planets

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/users', methods=["GET"])
def get_all_users():

    users = User.query.all()

    users = list(map(lambda item: item.serialize(), users))

    return jsonify(users), 200

@app.route('/users/favorites', methods=["GET"])
def get_favorites():
    favorites = Favorites.query.all()

    favorites = list(map(lambda item: item.serialize(), favorites))

    return jsonify(favorites), 200

#People GETS

@app.route('/people', methods=["GET"]) #people GET
def get_all_people():

    characters = People.query.all()

    characters = list(map(lambda item: item.serialize(), characters))

    return jsonify(characters), 200

@app.route('/people/<int:id>', methods=["GET"]) #people GET
def get_one_person(id):

    all_people = People.query.all()
    all_people = list(map(lambda item: item.serialize(), all_people))

    for person in all_people:

        if person["id"] == id:

            return jsonify(person), 200
        
#Final of People GETS



#Planets GETS

@app.route('/planets', methods={"GET"}) #planets GET
def get_all_planets():

    all_planets = Planet.query.all()

    all_planets = list(map(lambda item: item.serialize(), all_planets))

    return jsonify(all_planets), 200

@app.route('/planets/<int:id>', methods=["GET"]) #planet GET
def get_one_planet(id):

    all_planets = Planet.query.all()

    all_planets = list(map(lambda item: item.serialize(), all_planets))

    for one_planet in all_planets:
        if one_planet["id"] == id:
            return jsonify(one_planet), 200
        
#Final of Planets GETS

#Start of POSTS

@app.route('/favorite/planet/<int:planet_id>', methods=["POST"]) #planet POST
def add_planet_favorite(planet_id):

    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"Error" : "user_id is requiered"}), 400

    user = User.query.get(user_id)

    if not user:
        return jsonify({"Error" : "User not found"}), 400

    favorite_exist = Favorites.query.filter_by(
        user_id=user_id,
        planet_id=planet_id
    ).first()

    if favorite_exist:
        return jsonify("Sorry this planet is already in favorites.")
    
    new_favorite = Favorites(
        user_id = user_id,
        planet_id = planet_id
    )

    db.session.add(new_favorite)

    try:
        db.session.commit()
        return jsonify(f"Planet: {planet_id} added successfully to User: {user_id}")
    except Exception as error:
        db.session.rollback()
        return jsonify({"message" : f"Error: {error}"}), 500

@app.route('/favorite/people/<int:people_id>', methods=["POST"]) #people POST
def add_people_favorite(people_id):

    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"Error" : "user_id is requiered"}), 400

    user = User.query.get(user_id)

    if not user:
        return jsonify({"Error" : "User not found"}), 400

    favorite_exist = Favorites.query.filter_by(
        user_id=user_id,
        people_id=people_id
    ).first()

    if favorite_exist:
        return jsonify("Sorry this character is already in favorites.")
    
    new_favorite = Favorites(
        user_id = user_id,
        people_id = people_id
    )

    db.session.add(new_favorite)

    try:
        db.session.commit()
        return jsonify(f"Character: {people_id} added successfully to User: {user_id}")
    except Exception as error:
        db.session.rollback()
        return jsonify({"message" : f"Error: {error}"}), 500

#End of POSTS

#Start of DELETES

@app.route('/favorite/planet/<int:planet_id>', methods=["DELETE"]) #planet DELETE
def delete_planet(planet_id):

    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"Error" : "user_id is requiered"}), 400

    user = User.query.get(user_id)

    if not user:
        return jsonify({"Error" : "User not found"}), 400

    favorite = Favorites.query.filter_by(
        user_id = user_id,
        planet_id = planet_id
    ).first()

    if not favorite:
        return jsonify(f"This planet doesn't exist in User: {user_id}")

    db.session.delete(favorite)

    try:
        db.session.commit()
        return jsonify("Planet deleted successfully"), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"message" : f"Error: {error}"}), 400
    

@app.route('/favorite/people/<int:people_id>', methods=["DELETE"]) #people DELETE
def delete_people(people_id):

    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"Error" : "user_id is requiered"}), 400

    user = User.query.get(user_id)

    if not user:
        return jsonify({"Error" : "User not found"}), 400

    favorite = Favorites.query.filter_by(
        user_id = user_id,
        people_id = people_id
    ).first()

    if not favorite:
        return jsonify(f"This character doesn't exist in User: {user_id}")

    db.session.delete(favorite)

    try:
        db.session.commit()
        return jsonify("Character deleted successfully"), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"message" : f"Error: {error}"}), 400
    
#End of DELETES

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


@app.route('/people/population', methods=["GET"])
def people_population():
    
    characters = people()

    for person in characters:

        name = person["name"]
        height = person["height"]
        gender = person["gender"]
        birth_year = person["birth_year"]
        mass = person["mass"]
    
        new_person = People(
            name=name,
            height=height,
            gender=gender,
            birth_year=birth_year,
            mass=mass
        )

        db.session.add(new_person)

    try:
        db.session.commit()
        return jsonify("Data added successfully"), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"message": f"Error: {error}"}), 500
    
@app.route('/planets/population', methods=["GET"])
def planets_population():

    all_planets = planets()

    for planet_detail in all_planets:

        name = planet_detail["name"]
        population = planet_detail["population"]
        gravity = planet_detail["gravity"]
        diameter = planet_detail["diameter"]

        new_planet = Planet(
            name = name,
            population = population,
            gravity = gravity,
            diameter = diameter
        )

        db.session.add(new_planet)
    
    try:
        db.session.commit()
        return jsonify("Data added successfully"), 200
    except Exception as error:
        db.session.rollbalck()
        return jsonify({"message" : f"Error: {error}"}), 500