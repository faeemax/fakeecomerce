from flask import Flask, render_template, request, redirect, url_for, session, jsonify
# from flask_pymongo import PyMongo # Disabled for FakeMart experiment
# from bson.objectid import ObjectId # Disabled for FakeMart experiment
import secrets
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Load Data from JSON
def load_data():
    with open('data.json', 'r') as f:
        return json.load(f)

DATA = load_data()

# Helper to find product by ID
def get_product_by_id(product_id):
    for category in DATA['categories']:
        for product in category['products']:
            if product['id'] == product_id:
                return product
    return None

@app.route("/")
def home():
    # Flatten products for the "messy/modern" grid view
    all_products = []
    for category in DATA['categories']:
        for product in category['products']:
            # Add category name to product for context if needed
            p = product.copy()
            p['category'] = category['name']
            all_products.append(p)
    
    return render_template("home.html", products=all_products, store=DATA['store'])

@app.route("/product/<product_id>")
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return "Product not found (404 was healed by potion?)", 404
    return render_template("product.html", product=product, store=DATA['store'])

@app.route("/cart")
def cart():
    # Initialize cart in session if not exists
    if 'cart' not in session:
        session['cart'] = []
    
    cart_items = session['cart']
    total = sum(item['price'] for item in cart_items)
    
    return render_template("cart.html", cart_items=cart_items, total=total, store=DATA['store'])

@app.route("/add_to_cart/<product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = get_product_by_id(product_id)
    if not product:
         return redirect(url_for('home'))

    if 'cart' not in session:
        session['cart'] = []
    
    # Append to list (allow duplicates because why not?)
    session['cart'].append({
        "id": product['id'],
        "name": product['name'],
        "price": product['price'],
        "image": product.get("image_url", "https://placehold.co/100") # Fallback
    })
    session.modified = True
    
    # Check action type
    action = request.form.get('action')
    if action == 'add':
        # Stay on page (redirect to same product)
        return redirect(url_for('product_detail', product_id=product_id))
    
    # Default behavior (Acquire Asset) -> Go to Cart
    return redirect(url_for('cart'))

@app.route("/remove_from_cart/<product_id>", methods=["POST"])
def remove_from_cart(product_id):
    if 'cart' in session:
        # Remove first occurrence of the product
        for i, item in enumerate(session['cart']):
            if str(item['id']) == str(product_id):
                del session['cart'][i]
                break
        session.modified = True
    return redirect(url_for('cart'))

@app.route("/checkout", methods=["POST"])
def checkout():
    # Fake payment processing
    payment_mode = request.form.get('payment_mode')
    
    # Simulate glitch or success
    # Simulate glitch or success
    import random
    if random.random() < 0.1: # Reduced failure rate because glitches are annoying
        return "<h2>Payment Failed: Insufficient Good Vibes.</h2><a href='/cart'>Try Again</a>"
    
    session['cart'] = [] # Clear cart
    session.modified = True
    
    return redirect(url_for('thank_you'))

@app.route("/thankyou")
def thank_you():
    # Get IP Address (handling proxies)
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if user_ip and ',' in user_ip:
        user_ip = user_ip.split(',')[0].strip()
        
    return render_template("thankyou.html", ip=user_ip, store=DATA['store'])

# No init route needed for static JSON

if __name__ == "__main__":
    app.run(debug=True)
