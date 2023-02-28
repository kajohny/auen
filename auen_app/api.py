from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, json, Response
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func, and_, or_
from .models import User, Music, Author, Albums, Favourites, musics_schema, user_schema
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

@api.route('/profile/api/<email>', methods=["GET"])
def profile(email):
    user = User.query.filter_by(email = email).first()
    return user_schema.jsonify(user)

@api.route('/music/api/', methods=["GET"])
def music():
    musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img)\
        .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id).all()

    return musics_schema.jsonify(musics)

@api.route('/favourites/api/<id>', methods=["GET"])
def favourites(id):
    musics = db.session.query\
        (Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img)\
        .join(Albums, Albums.id == Music.album_id).join(Author, Music.author_id == Author.id)\
        .join(Favourites, and_(Favourites.music_id == Music.id, Favourites.user_id == id)).all()

    return musics_schema.jsonify(musics)