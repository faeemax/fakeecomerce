import json
import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
from flask_pymongo import PyMongo

# Load environment variables
load_dotenv()

# Initialize Flask app for PyMongo context
app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

def seed_codebase():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data.json')
    
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    with open(data_path, 'r') as f:
        data = json.load(f)

    categories = data.get('categories', [])
    store_name = data.get('store', {}).get('name', 'Store')

    print(f"Seeding products for {store_name}...")
    
    added_count = 0
    skipped_count = 0

    with app.app_context():
        # Ensure we can connect
        try:
            # simple command to check connection
            mongo.db.command('ping')
            print("Connected to MongoDB successfully.")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            return

        for category in categories:
            cat_name = category['name']
            products = category['products']
            
            for p in products:
                # Check for existing product by name
                existing = mongo.db.products.find_one({"name": p['name']})
                
                if existing:
                    skipped_count += 1
                    print(f"Skipping '{p['name']}' (already exists).")
                    continue
                
                # Construct product document
                product_doc = {
                    "name": p['name'],
                    "price": p['price'],
                    "category": cat_name,
                    "description": p.get('description', ''),
                    "image_url": p.get('image_url', ''),
                    "stock": p.get('stock', 0),
                    "type": p.get('type', 'physical'),
                    "seller_id": "system_seed",
                    "seller_name": "System Admin",
                    "date_added": datetime.utcnow()
                }
                
                mongo.db.products.insert_one(product_doc)
                added_count += 1
                print(f"Added '{p['name']}'")

    print(f"\nImport Summary:")
    print(f"Added: {added_count}")
    print(f"Skipped: {skipped_count}")

if __name__ == "__main__":
    seed_codebase()
