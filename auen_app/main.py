from this import d
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func, and_, or_
from .models import User, Music, Author, Favourites, Albums, Genres, Playlists
from . import db

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img, 
        db.session.query(Favourites.id)\
            .filter(and_(Music.id == Favourites.music_id, Favourites.user_id == current_user.id)).limit(1).label('is_favourite'))\
        .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id)\
        .filter(Music.id != None).order_by(func.random()).limit(15).all()

    else:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img)\
        .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id).limit(15).all()
        
    if request.method == "POST":
        title = request.form.get('search')
        search = "%{}%".format(title)

        print (title)

        musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name).join(Author, Music.author_id == Author.id)\
            .filter(or_(Music.music_title.ilike(search), Author.author_name.ilike(search))).all()
        return render_template("search.html", musics=musics)
    
    authors = Author.query.all()

    albums = db.session.query(Albums.id, Albums.album_title, Albums.album_img, Author.author_name).join(Author, Albums.author_id == Author.id).all()

    genres = Genres.query.all()

    return render_template('index.html', musics=musics, authors=authors, albums=albums, genres=genres)

@main.route('/album')
def album():
    authors = Author.query.all()
    albums = db.session.query(Albums.album_title, Albums.album_img, Author.author_name).join(Author, Albums.author_id == Author.id).all()
    
    return render_template('album.html', albums=albums, authors=authors)

@main.route('/artist')
def artist():
    authors = Author.query.all()
    
    return render_template('artist.html', authors=authors)

@main.route('/genre')
def genre():
    genres = Genres.query.all()
    
    return render_template('genres.html', genres=genres)

@main.route('/top_track')
def top_track():
    if current_user.is_authenticated:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img, 
        db.session.query(Favourites.id)\
            .filter(and_(Music.id == Favourites.music_id, Favourites.user_id == current_user.id)).limit(1).label('is_favourite'))\
        .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id)\
        .filter(Music.id != None).order_by(func.random()).limit(15).all()

    else:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img)\
        .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id).limit(15).all()
    
    return render_template('top_track.html', musics=musics)

@main.route('/artist/artist_single/<artist_id>', methods=["GET"])
def artist_single(artist_id):
    author_single = Author.query.filter_by(id=artist_id).first()

    if current_user.is_authenticated:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img, 
        db.session.query(Favourites.id)\
        .filter(and_(Music.id == Favourites.music_id, Favourites.user_id == current_user.id)).limit(1).label('is_favourite'))\
        .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id)\
        .filter(and_(Music.id != None, Author.id == artist_id)).order_by(func.random()).all()
    else:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img)\
            .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id)\
            .filter(Author.id == artist_id).all()

    authors_similar = Author.query.filter_by(genre_id=author_single.genre_id).filter(Author.id != artist_id).all()

    return render_template('artist_single.html', author_single=author_single, musics=musics, authors_similar=authors_similar)

@main.route('/album/album_single/<album_id>', methods=["GET"])
def album_single(album_id):
    album_single = Albums.query.filter_by(id=album_id).first()
    artist_single = db.session.query(Author.author_name).join(Albums, Albums.author_id == Author.id).filter(Albums.id == album_id).first()

    if current_user.is_authenticated:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img, 
        db.session.query(Favourites.id)\
        .filter(and_(Music.id == Favourites.music_id, Favourites.user_id == current_user.id)).limit(1).label('is_favourite'))\
        .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id)\
        .filter(and_(Music.id != None, Albums.id == album_id)).order_by(func.random()).all()
    else:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img)\
            .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id)\
            .filter(Albums.id == album_id).all()

    counter = 0

    for music in musics:
        counter += 1

    return render_template('album_single.html', album_single=album_single, artist_single=artist_single, musics=musics, counter=counter)

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, email=current_user.email)

@main.route('/profile/profile_edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        user = User.query.filter_by(email = current_user.email).first()

        if password == password_confirm:
            if check_password_hash(user.password, password):
                user.email = email
                user.name = name
                db.session.commit()

                return redirect(url_for('main.profile'))
            else:
                flash('Your password is incorrect')
        else:
            flash('Passwords do not match')
    
    return render_template('profile_edit.html', name=current_user.name, email=current_user.email)

@main.route('/profile/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == "POST":
        password = request.form.get('password')
        new_password = request.form.get('new_password')
        new_password2 = request.form.get('new_password2')

        user = User.query.filter_by(email=current_user.email).first()

        if check_password_hash(user.password, password):
            if new_password == new_password2:
                user.password = generate_password_hash(new_password, method='sha256')
                
                db.session.commit()

                return redirect(url_for('main.profile'))

            else:
                flash('Passwords do not match')
        else:
            flash('Your current pwd is incorrect')
    return render_template('profile_pwd_change.html')

@main.route("/profile/favourites", methods=["GET", "POST"])
@login_required
def favourites():
    musics = db.session.query\
        (Music.id, Music.music_title, Music.music_source, Albums.album_title, Albums.album_img, Author.author_name)\
        .join(Albums, Albums.id == Music.album_id)\
        .join(Author, Author.id == Music.author_id)\
        .join(Favourites, and_(Favourites.music_id == Music.id, Favourites.user_id == current_user.id)).all()
    
    if request.method == "POST":
        music_id = request.form.get('music_id')
        favourite = Favourites.query.filter_by(music_id=music_id, user_id=current_user.id).first()

        db.session.delete(favourite)
        db.session.commit()

        return redirect(url_for('main.favourites'))
    return render_template('favourite.html', musics=musics)

@main.route("/favourites/add", methods=["POST"])
@login_required
def add_favourites():
    music_id = request.form.get('music_id')

    favourite = Favourites(user_id=current_user.id, music_id=music_id)
        
    db.session.add(favourite)
    db.session.commit()

    return "added"

@main.route("/favourites/remove", methods=["POST"])
@login_required
def remove_favourites():
    music_id = request.form.get('music_id')
    favourite = Favourites.query.filter_by(music_id=music_id, user_id=current_user.id).first()

    db.session.delete(favourite)
    db.session.commit()

    return "removed"

@main.route('/profile/playlist_user')
@login_required
def playlist_user():
    favourites = Favourites.query.filter_by(user_id=current_user.id).all()
    playlists = Playlists.query.filter_by(user_id=current_user.id).all()

    playlists_count = Playlists.query.filter(Playlists.music_id != None).filter_by(user_id=current_user.id).all()
    counter_f = 0
    counter_p = 0

    for favourite in favourites:
        counter_f += 1
    
    for playlist in playlists_count:
        counter_p += 1
    
    return render_template('add_playlist.html', playlists=playlists, counter_f=counter_f, counter_p=counter_p)

@main.route('/profile/create_playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    if request.method == "POST":
        playlist_name = request.form.get('playlist_name')

        new_playlist = Playlists(user_id=current_user.id, playlist_name=playlist_name)

        db.session.add(new_playlist)
        db.session.commit()

        return redirect(url_for('main.playlist_user'))
    return render_template('create_playlist.html')