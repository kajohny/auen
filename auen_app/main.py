from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func, and_, or_, desc
from .models import User, Music, Author, Favourites, Albums, Genres, Playlists, Audios, PlaylistMusic, Releases, Followers
from . import db
from sqlalchemy import cast, Date
import os
import re
from PIL import Image

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

        if current_user.is_authenticated:
            musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img, 
            db.session.query(Favourites.id)\
            .filter(and_(Music.id == Favourites.music_id, Favourites.user_id == current_user.id)).limit(1).label('is_favourite'))\
            .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id)\
            .filter(Music.id != None).filter(or_(Music.music_title.ilike(search), Author.author_name.ilike(search))).all()
        else:
            musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img)\
                .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id)\
                .filter(or_(Music.music_title.ilike(search), Author.author_name.ilike(search))).all()
        return render_template("search.html", musics=musics)
    
    authors = Author.query.all()

    albums = db.session.query(Albums.id, Albums.album_title, Albums.album_img, Author.author_name).join(Author, Albums.author_id == Author.id).all()

    genres = Genres.query.all()

    artists = User.query.filter_by(isartist=True).all()

    return render_template('index.html', musics=musics, authors=authors, albums=albums, genres=genres, artists=artists)

@main.route('/album')
def album():
    authors = Author.query.all()
    albums = db.session.query(Albums.album_title, Albums.album_img, Author.author_name).join(Author, Albums.author_id == Author.id).all()
    
    return render_template('album.html', albums=albums, authors=authors)

@main.route('/artist')
def artist():
    authors = Author.query.all()
    
    return render_template('artist.html', authors=authors)

@main.route('/genres')
def genre():
    return render_template('genres.html')

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

    # if current_user.is_authenticated:
    #     musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img, 
    #     db.session.query(Favourites.id)\
    #     .filter(and_(Music.id == Favourites.music_id, Favourites.user_id == current_user.id)).limit(1).label('is_favourite'))\
    #     .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id)\
    #     .filter(and_(Music.id != None, Author.id == artist_id)).order_by(func.random()).all()
    # else:
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

@main.route('/genres/genres_single/<genre_id>', methods=["GET"])
def genres_single(genre_id):
    genre = Genres.query.filter_by(id=genre_id).first()

    musics = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img)\
        .join(Author, Author.id == Music.author_id)\
        .join(Albums, Albums.id == Music.album_id)\
        .join(Genres, Genres.id == Music.genre_id).filter(Genres.id == genre_id).order_by(func.random()).all()
    
    return render_template('genres_single.html', genre=genre, musics=musics)

@main.route('/profile')
@login_required
def profile():
    user = User.query.filter_by(id = current_user.id).first()
    return render_template('profile.html', user=user)

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

    playlists = db.session.query(Playlists.playlist_name, Playlists.id, PlaylistMusic.playlist_id, func.count(PlaylistMusic.playlist_id).label('counter'))\
        .join(PlaylistMusic, PlaylistMusic.playlist_id == Playlists.id)\
        .filter(Playlists.user_id == current_user.id).group_by(Playlists.id, PlaylistMusic.playlist_id, Playlists.playlist_name)
    
    counter_f = 0

    for favourite in favourites:
        counter_f += 1
    
    return render_template('add_playlist.html', playlists=playlists, counter_f=counter_f)

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

@main.route('/profile/playlist_user/<playlist_id>', methods=["GET", "POST"])
@login_required
def playlist_music(playlist_id):
    playlist_single = Playlists.query.filter_by(id = playlist_id).first()

    musics = db.session.query(Music.id, Music.music_title, Music.music_source, Albums.album_title, Albums.album_img)\
        .join(Albums, Albums.id == Music.album_id).join(PlaylistMusic, PlaylistMusic.music_id == Music.id)\
        .filter(PlaylistMusic.playlist_id == playlist_id)
    
    # musics_playlist = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img)\
    #     .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id)\
    #     .filter(Music.id != None).order_by(func.random()).limit(15).all()
    
    musics_playlist = db.session.query(Music.id, Music.music_title, Music.music_source, Author.author_name, Albums.album_img, 
        db.session.query(PlaylistMusic.id)\
            .filter(and_(Music.id == PlaylistMusic.music_id, PlaylistMusic.playlist_id == playlist_id)).limit(1).label('is_playlist'))\
        .join(Author, Music.author_id == Author.id).join(Albums, Albums.id == Music.album_id)\
        .filter(Music.id != None).limit(15).all()
    
    return render_template('playlist_music.html', playlist_single=playlist_single, musics=musics, musics_playlist=musics_playlist)

@main.route("/playlist/add", methods=["POST"])
@login_required
def add_playlist():
    music_id = request.form.get('music_id')
    playlist_id = request.form.get('playlist_id')

    playlist = PlaylistMusic(playlist_id=playlist_id, music_id=music_id)
        
    db.session.add(playlist)
    db.session.commit()

    return "added"

@main.route("/playlist/remove", methods=["POST"])
@login_required
def remove_playlist():
    music_id = request.form.get('music_id')
    playlist_id = request.form.get('playlist_id')
    playlist = PlaylistMusic.query.filter_by(music_id=music_id, playlist_id=playlist_id).first()

    db.session.delete(playlist)
    db.session.commit()

    return "removed"

@main.route('/profile/upload', methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        files = request.files.getlist('file')
        titles = request.form.getlist('title')
        
        if(len(files) > 1):
            album_title = request.form.get('album_title')
        else:
            album_title = request.form.get('title')

        img_file = request.files['img-file']

        if img_file.filename:
            img_file.save(os.path.join("auen_app/static/images/album", img_file.filename))
            release = Releases(album_title = album_title, album_img = 'images/album/' + img_file.filename, author_id=current_user.id)
        else:
            release = Releases(album_title = album_title, album_img = 'images/album/images.jfif', author_id=current_user.id)
        db.session.add(release)
        db.session.commit()

        release = Releases.query.filter_by(album_title=album_title).first()

        for i in range(len(files)):
            fixedFilename = re.sub('[^A-Za-z0-9.]+', '', files[i].filename)
            files[i].save(os.path.join("auen_app/static/audio", fixedFilename))
            add_audio = Audios(title = titles[i], source="/static/audio/" + fixedFilename, album_id = release.id, artist_id = current_user.id)
            db.session.add(add_audio)
            db.session.commit()
        return render_template('upload.html')
    return render_template('upload.html')

@main.route('/artists/<artist_id>', methods=["GET"])
def single_artist(artist_id):
    artist_single = User.query.filter_by(id=artist_id).first()

    audios = db.session.query(Audios.id, Audios.title, Audios.source, User.name, Releases.album_img)\
            .join(User, Audios.artist_id == User.id).join(Releases, Releases.id == Audios.album_id)\
            .filter(User.id == artist_id).all()
    
    is_followed = Followers.query.filter_by(follower_id=current_user.id, followed_id=artist_id).first()
    followed_all = Followers.query.filter_by(followed_id=artist_id).all()
    follower_all = Followers.query.filter_by(follower_id=artist_id).all()

    counter_audio = 0
    counter_followed = 0
    counter_followers = 0

    for audio in audios:
        counter_audio += 1

    for i in followed_all:
        counter_followed += 1

    for i in follower_all:
        counter_followers += 1

    return render_template('artist_page.html', artist_single=artist_single, audios=audios, counter_audio=counter_audio, 
                           counter_followed=counter_followed, counter_followers=counter_followers, is_followed=is_followed)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/edit_pfp', methods=["GET", "POST"])
@login_required
def edit_pfp():
    if request.method == "POST":
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            file.save(os.path.join("auen_app/static/images/pfp", file.filename))
            image = Image.open('auen_app/static/images/pfp/' + file.filename)
            new_image = image.resize((360, 360))
            new_image.save(os.path.join("auen_app/static/images/pfp", file.filename))
            user = User.query.filter_by(id = current_user.id).first()
            user.image = "/images/pfp/" + file.filename
            db.session.commit()
            return render_template("profile.html", user=user)
        else:
            return redirect(url_for('main.profile'))
        
@main.route('/following/follow', methods=["POST"])
@login_required
def follow():
    followed_id = request.form.get('followed_id')

    follower = Followers(follower_id=current_user.id, followed_id=followed_id)
    db.session.add(follower)
    db.session.commit()

    return "followed"


@main.route('/following/unfollow', methods=["POST"])
@login_required
def unfollow():
    followed_id = request.form.get('followed_id')

    follower = Followers.query.filter_by(follower_id=current_user.id, followed_id=followed_id).first()
    db.session.delete(follower)
    db.session.commit()

    return "unfollowed"

@main.route('/feed', methods=["GET"])
@login_required
def feed():
    musics = db.session.query(Audios.id, Audios.title, Audios.source, User.name, Releases.album_img, Releases.album_title, 
                              (Audios.time_added.cast(Date)).label('time_added'))\
            .join(User, Audios.artist_id == User.id).join(Releases, and_(Releases.id == Audios.album_id, Releases.author_id == User.id))\
            .join(Followers, Followers.followed_id == User.id).filter(Followers.follower_id == current_user.id)\
            .group_by(Audios.id, User.name, Audios.title, Audios.source, Audios.time_added, Releases.album_title, 
                      Releases.album_img).order_by(desc('time_added')).all()
    

    return render_template("feed.html", musics=musics)