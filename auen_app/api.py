from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, json, Response
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func, and_, or_
from .models import User, Music, Author, Albums, Favourites, Playlists, PlaylistMusic, musics_schema, user_schema, playlist_schema, albums_schema 
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
        isartist = request.form['isartist']
        image = "/images/pfp/pfp_standard.jpg"

        if isartist == "artist":
            isartist = True
        else:
            isartist = False

        user = User.query.filter_by(email=email).first()
        if user:
            print("Email already exists")
        else:
            if password != password_confirm:
                return jsonify(['passwords do not match'])
            else:
                reg_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), image=image, isartist=isartist)
                db.session.add(reg_user)
                db.session.commit()
                return jsonify(['success'])
    return jsonify(['registration'])


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

@api.route('/favouritesAdd/api/<id>', methods=["POST"])
def add_favourites(id):
    if request.method == "POST":
        music_id = request.form['music_id']

        favourite = Favourites(user_id=id, music_id=music_id)

        db.session.add(favourite)
        db.session.commit()

        return jsonify(['success'])
    
    return jsonify(['add to fav'])

@api.route('/favouritesRemove/api/<id>', methods=["POST"])
def remove_favourites(id):
    if request.method == "POST":
        music_id = request.form['music_id']

        favourite = Favourites.query.filter_by(user_id=id, music_id=music_id).first()   

        db.session.delete(favourite)
        db.session.commit()

        return jsonify(['success'])
    
    return jsonify(['remove fav'])

@api.route('/playlist_user/api/<id>', methods=["GET"])
def playlist_user(id):
    playlists = Playlists.query.filter_by(user_id = id).all()
    
    return playlist_schema.jsonify(playlists)

@api.route('/playlist_songs/api/<playlist_id>', methods=["GET"])
def playlist_songs(playlist_id):
    musics = db.session.query(Music.id, Music.music_title, Music.music_source, Albums.album_title, Albums.album_img)\
        .join(Albums, Albums.id == Music.album_id).join(PlaylistMusic, PlaylistMusic.music_id == Music.id)\
        .filter(PlaylistMusic.playlist_id == playlist_id)
    
    return musics_schema.jsonify(musics)

@api.route('/create_playlist/api/<id>', methods=["POST"])
def create_playlist(id):
    if request.method == "POST":
        playlist_name = request.form['playlist_name']

        new_playlist = Playlists(user_id=id, playlist_name=playlist_name)

        db.session.add(new_playlist)
        db.session.commit()

        return jsonify(['success'])
    return jsonify(['create playlist'])

@api.route('/playlist_add/api/', methods=["POST"])
def playlist_add():
    if request.method == "POST":
        music_id = request.form['music_id']
        playlist_id = request.form['playlist_id']

        playlist = PlaylistMusic(playlist_id=playlist_id, music_id=music_id)
        
        db.session.add(playlist)
        db.session.commit()

        return jsonify(['success'])
    return jsonify(['add to playlist'])

@api.route('/playlist_remove/api/', methods=["POST"])
def playlist_remove():
    if request.method == "POST":
        music_id = request.form['music_id']
        playlist_id = request.form['playlist_id']

        playlist = PlaylistMusic.query.filter_by(music_id=music_id, playlist_id=playlist_id).first()
        
        db.session.delete(playlist)
        db.session.commit()

        return jsonify(['success'])
    return jsonify(['remove from playlist'])

@api.route('/albums/api', methods=["GET"])
def albums():
    albums = db.session.query(Albums.id, Albums.album_title, Albums.album_img, Author.author_name).join(Author, Albums.author_id == Author.id).all()

    return albums_schema.jsonify(albums)

@api.route('/album_songs/api/<album_id>', methods=["GET"])
def album_songs(album_id):
    musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img)\
            .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id)\
            .filter(Albums.id == album_id).all()

    return musics_schema.jsonify(musics)
