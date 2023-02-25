from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func, and_, or_
from .models import User, UserSchema, user_schema
from . import db

api = Blueprint('api', __name__)

@api.route('/login/api', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify(["error"])
        
        print('hello')
        return jsonify(["success"])
    return jsonify(['hello'])

@api.route('/registration/api', methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        user = User.query.filter_by(email=email).first()
        if user:
            print("Email already exists")
        else:
            reg_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
            db.session.add(reg_user)
            db.session.commit()
            print("success")