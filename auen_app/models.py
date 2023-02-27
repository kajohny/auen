from flask_login import UserMixin
from . import db
from . import ma

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing':True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    image = db.Column(db.String(100))
    isartist = db.Column(db.Boolean, default=False)

class UserSchema(ma.Schema) :
    class Meta:
        fields = ('id', 'name', 'email', 'password', 'image', 'isartist')   

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class Genres(db.Model):
    __tablename__ = 'genres'
    __table_args__ = {'extend_existing':True}
    id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String(255))
    genre_img = db.Column(db.String(255))

class Author(db.Model):
    __tablename__ = 'author'
    __table_args__ = {'extend_existing':True}
    id = db.Column(db.Integer, primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
    author_name = db.Column(db.String(255), unique=True)
    author_photo = db.Column(db.String(255))

class Albums(db.Model):
    __tablename__ = 'albums'
    __table_args__ = {'extend_existing':True}
    id = db.Column(db.Integer, primary_key=True)    
    album_title = db.Column(db.String(255))
    album_img = db.Column(db.String(255))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))    

class Music(db.Model):
    __tablename__ = 'music'
    __table_args__ = {'extend_existing':True}
    id = db.Column(db.Integer, primary_key=True)
    music_title = db.Column(db.String(255))
    music_source = db.Column(db.String(255))
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'))

class Favourites(db.Model):
    __tablename__ = 'favourites'
    __table_args__ = {'extend_existing':True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    music_id = db.Column(db.Integer, db.ForeignKey('music.id'))

class Playlists(db.Model):
    __tablename__ = 'playlists'
    __table_args__ = {'extend_existing':True}
    id = db.Column(db.Integer, primary_key=True)
    playlist_name = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    music_id = db.Column(db.Integer, db.ForeignKey('music.id'))

class Audios(db.Model):
    __tablename__ = 'audios'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    source = db.Column(db.String(255))
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'))




