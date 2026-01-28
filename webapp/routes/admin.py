from flask import Blueprint, render_template, redirect, url_for
from bson.objectid import ObjectId
from .. import mongo, DATA
from ..utils import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/admax")
@admin_required
def dashboard():
    total_orders = mongo.db.orders.count_documents({})
    total_users = mongo.db.users.count_documents({})
    
    pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$total"}}}
    ]
    result = list(mongo.db.orders.aggregate(pipeline))
    total_revenue = round(result[0]['total'], 2) if result else 0.0
    
    recent_orders = list(mongo.db.orders.find().sort("date", -1).limit(10))
    for order in recent_orders:
        order['_id'] = str(order['_id'])
        
    all_products = list(mongo.db.products.find())
    for p in all_products:
        p['id'] = str(p['_id'])

    # --- Top Earners Logic ---
    all_orders_for_stats = list(mongo.db.orders.find())
    
    seller_earnings = {} 
    
    product_seller_map = {str(p['_id']): p.get('seller_name', 'Unknown') for p in all_products}

    for order in all_orders_for_stats:
        for item in order.get('items', []):
            item_total = float(item.get('price', 0))
            
            seller_name = item.get('seller_name')
            if not seller_name:
                p_id = item.get('id')
                seller_name = product_seller_map.get(p_id, 'System/Unknown')
            
            if seller_name in seller_earnings:
                seller_earnings[seller_name] += item_total
            else:
                seller_earnings[seller_name] = item_total
                
    # --- Product Sales Logic ---
    product_sales_map = {}
    for order in all_orders_for_stats:
        for item in order.get('items', []):
            p_id = item.get('id')
            p_price = float(item.get('price', 0))
            
            if p_id in product_sales_map:
                product_sales_map[p_id] += p_price
            else:
                product_sales_map[p_id] = p_price
                
    for p in all_products:
        p_id = str(p['_id'])
        p['total_sales'] = round(product_sales_map.get(p_id, 0.0), 2)
    
    top_earners = sorted(seller_earnings.items(), key=lambda x: x[1], reverse=True)
    max_earnings = top_earners[0][1] if top_earners else 1.0
    
    # --- Payment Method Stats ---
    payment_pipeline = [
        {"$group": {"_id": "$payment_mode", "total": {"$sum": "$total"}}}
    ]
    payment_stats_raw = list(mongo.db.orders.aggregate(payment_pipeline))
    payment_stats = [{"mode": p['_id'] or "Unknown", "total": round(p['total'], 2)} for p in payment_stats_raw]
    
    sellers = list(mongo.db.users.find({"role": "seller"}))
    
    max_sales = max([p.get('total_sales', 0) for p in all_products]) if all_products else 1.0
        
    return render_template("admin_dashboard.html", 
                           total_orders=total_orders, 
                           total_revenue=total_revenue, 
                           total_users=total_users,
                           orders=recent_orders,
                           products=all_products,
                           store=DATA['store'],
                           top_earners=top_earners,
                           payment_stats=payment_stats,
                           sellers=sellers,
                           max_earnings=max_earnings,
                           max_sales=max_sales)

@admin_bp.route("/delete_user/<user_id>")
@admin_required
def delete_user(user_id):
    mongo.db.users.delete_one({"_id": ObjectId(user_id)})
    return redirect(url_for('admin.dashboard'))

@admin_bp.route("/delete_product/<product_id>")
@admin_required
def delete_product(product_id):
    mongo.db.products.delete_one({"_id": ObjectId(product_id)})
    return redirect(url_for('admin.dashboard'))
