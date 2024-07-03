from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    restaurantpizzas = db.relationship('RestaurantPizza', back_populates='restaurant',cascade="all, delete")

    # add serialization rules
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'restaurantpizzas': [rp.to_dict() for rp in self.restaurantpizzas]
        }
    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurantpizzas = db.relationship('RestaurantPizza',back_populates='pizza',cascade="all, delete")

    # add serialization rules
    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'ingredients': self.ingredients,
                'restaurantpizzas': [rp.to_dict() for rp in self.restaurantpizzas]
                }

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # add pizza relationships
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    pizza = db.relationship('Pizza',back_populates='restaurantpizzas',cascade="all, delete")

    # add restaurant relationships
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    restaurant = db.relationship('Restaurant',back_populates='restaurantpizzas')

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
    
    # add serialization rules
    def to_dict(self):
        return {'id': self.id,
                'price': self.price,
                'pizza': self.pizza.to_dict(),
                'restaurant': self.restaurant.to_dict(),
                }

    #add price attribute validation
    @validates('price')
    def validate_price(self,key, price):
        if price < 1 or price > 30:
            raise ValueError('Price must be between 1 and 30')
        return price 
    