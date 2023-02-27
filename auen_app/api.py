from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, json, Response
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func, and_, or_
from .models import User, UserSchema, user_schema, Music, Author, Albums, musics_schema
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
    
    musics_list = []
    
    for music in musics:
        musics_list.append(music)   

    json_string = json.dumps(str(musics_list), ensure_ascii=False)

    response = Response(json_string,content_type="application/json; charset=utf-8" )
    
    return response

@api.route('/music_available/api/', methods=["GET"])
def music_available():
    musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img)\
        .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id).filter(Music.music_source.ilike("music%")).all()
    
    musics_list = []
    
    for music in musics:
        musics_list.append(music)   

    json_string = json.dumps(str(musics_list), ensure_ascii=False)

    response = Response(json_string,content_type="application/json; charset=utf-8" )
    
    return response