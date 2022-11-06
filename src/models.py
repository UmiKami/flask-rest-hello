import datetime
from email.policy import default
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False, default=True)
    watchlist = db.relationship('Watchlist')
    post = db.relationship('Post')

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Watchlist(db.Model):
    __tablename__ = 'Watchlist'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    stock = db.Column(db.String(10), unique=False, nullable=False)

    user = db.relationship('User', foreign_keys = [user_id])

    def __repr__(self):
        return '<Watchlist %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "stock": self.stock
            # do not serialize the password, its a security breach
        }
class Post(db.Model):
    __tablename__ = 'Post'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    header = db.Column(db.String(60), nullable=False)
    body = db.Column(db.String(60), nullable=False)
    time_created = db.Column(db.DateTime, default=datetime.datetime.now())

    user = db.relationship('User', foreign_keys = [user_id])

    def __repr__(self):
        return '<Post %r>' % self.header

    def serialize(self):
        return {
            "id": self.id,
            "header": self.header,
            "body": self.body,
            "time_created": self.time_created
        }

    