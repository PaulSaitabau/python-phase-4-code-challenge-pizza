#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from sqlalchemy.exc import IntegrityError

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

migrate = Migrate(app, db)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([{'id': restaurant.id, 'name': restaurant.name, 'address': restaurant.address} for restaurant in restaurants]), 200

@app.route('/restaurants/<int:id>', methods=['GET'])
def restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    
    restaurant_data = {
        'id': restaurant.id,
        'name': restaurant.name,
        'address': restaurant.address,
        'restaurant_pizzas': []
    }
    
    for rp in restaurant.restaurantpizzas:
        pizza_data = {
            'id': rp.id,
            'restaurant_id': rp.restaurant_id,
            'pizza_id': rp.pizza_id,
            'price': rp.price,
            'pizza': {
                'id': rp.pizza.id,
                'name': rp.pizza.name,
                'ingredients': rp.pizza.ingredients
            }
        }
        restaurant_data['restaurant_pizzas'].append(pizza_data)
    
    return jsonify(restaurant_data)

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404
        
        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        
        db.session.delete(restaurant)
        db.session.commit()
        
        return jsonify({'message': 'Restaurant deleted successfully'}), 204
    
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Integrity error occurred'}), 500

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([{'id': pizza.id, 'name': pizza.name, 'ingredients': pizza.ingredients} for pizza in pizzas])

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    if not all(key in data for key in ('price', 'pizza_id', 'restaurant_id')):
        return jsonify({'errors': ['price, pizza_id, and restaurant_id are required']}), 400
    
    pizza = Pizza.query.get(data['pizza_id'])
    restaurant = Restaurant.query.get(data['restaurant_id'])

    if not pizza or not restaurant:
        return jsonify({'errors': ['Pizza or Restaurant not found']}), 400
    
    if not 1 <= data['price'] <= 30:
        return jsonify({'errors': ['Price must be between 1 and 30']}), 400

    restaurant_pizza = RestaurantPizza(
        price=data['price'],
        pizza=pizza,
        restaurant=restaurant
    )

    try:
        db.session.add(restaurant_pizza)
        db.session.commit()

        response_data = {
            'id': restaurant_pizza.id,
            'price': restaurant_pizza.price,
            'pizza': {
                'id': pizza.id,
                'name': pizza.name,
                'ingredients': pizza.ingredients
            },
            'pizza_id': pizza.id,
            'restaurant': {
                'id': restaurant.id,
                'name': restaurant.name,
                'address': restaurant.address
            },
            'restaurant_id': restaurant.id
        }

        return jsonify(response_data), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)
