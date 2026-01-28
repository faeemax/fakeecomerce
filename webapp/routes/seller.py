from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import datetime
from .. import mongo, DATA
from ..utils import login_required

seller_bp = Blueprint('seller', __name__)

@seller_bp.route("/add")
@login_required
def seller_dashboard():
    user_id = session.get('user_id')
    
    my_products = list(mongo.db.products.find({"seller_id": user_id}))
    for p in my_products:
        p['id'] = str(p['_id'])
        
    total_sales = 0
    total_earnings = 0.0
    
    my_product_ids = [p['id'] for p in my_products]
    
    all_orders = mongo.db.orders.find()
    for order in all_orders:
        for item in order.get('items', []):
            if item.get('id') in my_product_ids:
                total_sales += 1
                total_earnings += float(item.get('price', 0))

    return render_template("seller_dashboard.html", 
                           products=my_products, 
                           total_sales=total_sales, 
                           total_earnings=round(total_earnings, 2),
                           store=DATA['store'])

@seller_bp.route("/add_product_action", methods=["POST"])
@login_required
def add_product_action():
    new_product = {
        "name": request.form.get("name"),
        "price": float(request.form.get("price")),
        "category": request.form.get("category"),
        "description": request.form.get("description"),
        "image_url": request.form.get("image_url") or "https://placehold.co/400x300",
        "seller_id": session['user_id'],
        "seller_name": session['username'],
        "date_added": datetime.utcnow()
    }
    mongo.db.products.insert_one(new_product)
    return redirect(url_for('seller.seller_dashboard'))
