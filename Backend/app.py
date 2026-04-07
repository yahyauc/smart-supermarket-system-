from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db
from models.user import User
from models.product import Product
from models.order import Order
from models.order_item import OrderItem
from routes.auth import auth_bp
from routes.products import products_bp
from routes.orders import orders_bp
from routes.stats import stats_bp
from routes.chatbot import chatbot_bp
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure instance folder exists
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp,     url_prefix="/api")
    app.register_blueprint(products_bp, url_prefix="/api")
    app.register_blueprint(orders_bp,   url_prefix="/api")
    app.register_blueprint(stats_bp,    url_prefix="/api")
    app.register_blueprint(chatbot_bp,  url_prefix="/api")

    @app.route("/")
    def home():
        return jsonify({"message": "Smart Supermarket API is running", "version": "2.0"})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    with app.app_context():
        db.create_all()
        _seed_data()

    return app


def _seed_data():
    """Insert sample data only if the database is empty."""

    if User.query.count() == 0:
        admin = User(username="admin", email="admin@smart.ma", role="admin")
        admin.set_password("admin123")

        customer = User(username="abdo", email="abdo@smart.ma", role="customer")
        customer.set_password("abdo123")

        db.session.add_all([admin, customer])
        db.session.commit()

    if Product.query.count() == 0:
        products = [
            Product(name="Whole Milk 1L",      category="Dairy",    price=8.50,  stock=30, description="Fresh whole milk"),
            Product(name="Sourdough Bread",    category="Bakery",   price=12.00, stock=20, description="Artisan sourdough"),
            Product(name="Apple Juice 1L",     category="Drinks",   price=15.00, stock=25, description="100% natural juice"),
            Product(name="Cheddar Cheese",     category="Dairy",    price=35.00, stock=3,  description="Aged cheddar"),
            Product(name="Olive Oil 500ml",    category="Pantry",   price=55.00, stock=15, description="Extra virgin"),
            Product(name="Basmati Rice 1kg",   category="Pantry",   price=22.00, stock=40, description="Long grain rice"),
            Product(name="Free Range Eggs x6", category="Dairy",    price=18.00, stock=2,  description="Farm fresh eggs"),
            Product(name="Orange Juice 1L",    category="Drinks",   price=14.00, stock=18, description="Freshly squeezed"),
            Product(name="Pasta 500g",         category="Pantry",   price=9.00,  stock=35, description="Durum wheat pasta"),
            Product(name="Greek Yogurt 500g",  category="Dairy",    price=20.00, stock=0,  description="Creamy Greek yogurt"),
        ]
        db.session.add_all(products)
        db.session.commit()


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)