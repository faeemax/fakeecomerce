from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import datetime
from .. import mongo

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = "seller" # Default role
        
        if mongo.db.users.find_one({"username": username}):
             return render_template("register.html", error="Username already exists")
        
        user = {
            "username": username,
            "password": password, 
            "role": role,
            "created_at": datetime.utcnow()
        }
        mongo.db.users.insert_one(user)
        return redirect(url_for('auth.login'))
        
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = mongo.db.users.find_one({"username": username, "password": password})
        
        if user:
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard')) 
            else:
                return redirect(url_for('seller.seller_dashboard'))
        else:
            return render_template("login.html", error="Invalid credentials")
            
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('shop.home'))
