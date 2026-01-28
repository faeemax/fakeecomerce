import os
import json
from flask import Flask
from flask_pymongo import PyMongo
from .config import Config

mongo = PyMongo()
DATA = {}

def load_data():
    try:
        # Data is loaded inside app context in create_app
        return {}
    except Exception as e:
        print(f"Warning: Could not load data: {e}")
        return {}

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    app.config.from_object(config_class)

    mongo.init_app(app)

    # Load global data
    # Load global data
    global DATA
    with app.app_context():
        config_data = mongo.db.site_config.find_one()
        if config_data:
            DATA = {
                "store": config_data.get('store'),
                "categories": config_data.get('categories')
            }
        else:
             DATA = {
                "store": {
                    "name": "FakeMart (Rescue Mode)",
                    "currency": "COINS",
                    "payment_modes": ["Emergency Pay"]
                },
                "categories": []
            }

    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.shop import shop_bp
    from .routes.seller import seller_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(admin_bp)

    return app
