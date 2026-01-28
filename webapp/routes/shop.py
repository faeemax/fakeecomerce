from flask import Blueprint, render_template, session, redirect, url_for, request
from bson.objectid import ObjectId
from datetime import datetime
from .. import mongo, DATA

shop_bp = Blueprint('shop', __name__)

def get_product_by_id(product_id):
    try:
        product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        if product:
            product['id'] = str(product['_id'])
            return product
    except:
        pass
    return None

@shop_bp.route("/")
def home():
    products = list(mongo.db.products.find())
    for p in products:
        p['id'] = str(p['_id'])
    
    return render_template("home.html", products=products, store=DATA['store'])

@shop_bp.route("/product/<product_id>")
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return "Product not found", 404
    return render_template("product.html", product=product, store=DATA['store'])

@shop_bp.route("/cart")
def cart():
    if 'cart' not in session:
        session['cart'] = []
    
    cart_items = session['cart']
    total = sum(item['price'] for item in cart_items)
    
    return render_template("cart.html", cart_items=cart_items, total=total, store=DATA['store'])

@shop_bp.route("/add_to_cart/<product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = get_product_by_id(product_id)
    if not product:
         return redirect(url_for('shop.home'))

    if 'cart' not in session:
        session['cart'] = []
    
    session['cart'].append({
        "id": product['id'],
        "name": product['name'],
        "price": product['price'],
        "image": product.get("image_url", "https://placehold.co/100"),
        "seller_id": product.get("seller_id"),
        "seller_name": product.get("seller_name")
    })
    session.modified = True
    
    action = request.form.get('action')
    if action == 'add':
        return redirect(url_for('shop.product_detail', product_id=product_id))
    
    return redirect(url_for('shop.cart'))

@shop_bp.route("/remove_from_cart/<product_id>", methods=["POST"])
def remove_from_cart(product_id):
    if 'cart' in session:
        for i, item in enumerate(session['cart']):
            if str(item['id']) == str(product_id):
                del session['cart'][i]
                break
        session.modified = True
    return redirect(url_for('shop.cart'))

@shop_bp.route("/checkout", methods=["POST"])
def checkout():
    payment_mode = request.form.get('payment_mode')
    
    import random
    if random.random() < 0.1: 
        return "<h2>Payment Failed: Insufficient Good Vibes.</h2><a href='/cart'>Try Again</a>"
    
    cart_items = session.get('cart', [])
    if not cart_items:
        return redirect(url_for('shop.home'))
        
    total = sum(item['price'] for item in cart_items)
    
    order = {
        "items": cart_items,
        "total": total,
        "payment_mode": payment_mode,
        "date": datetime.utcnow(),
        "status": "Completed"
    }
    mongo.db.orders.insert_one(order)
    
    session['cart'] = []
    session.modified = True
    
    return redirect(url_for('shop.thank_you'))

@shop_bp.route("/thankyou")
def thank_you():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if user_ip and ',' in user_ip:
        user_ip = user_ip.split(',')[0].strip()
        
    return render_template("thankyou.html", ip=user_ip, store=DATA['store'])
