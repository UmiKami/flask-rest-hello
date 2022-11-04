"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from email import message
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Watchlist
import random
import smtplib
from email.message import EmailMessage
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def display_all_users():
    users = User.query.all();
    all_users = list(map(lambda user: user.serialize(), users))

    return jsonify(all_users), 200

@app.route('/signup', methods=['POST'])
def create_user():
    request_body = request.get_json(force=True)

    newUser = User(email=request_body["email"], password=request_body["password"])
    print(newUser)
    db.session.add(newUser)
    db.session.commit()

    return jsonify("User created"), 200

@app.route('/reset-password', methods=['POST'])
def send_email():
    global pw_code
    request_body = request.get_json(force=True)

    email = request_body["email"]

    emailExists = User.query.filter_by(email=email).first()
    admin_email = "ernestox.061@gmail.com"
    admin_password = "feaunqxmnzhufkzl"

    reset_code = random.randint(1000, 99999)

    if emailExists:
        message = EmailMessage()
        message["Subject"] = "reset your password"
        message["From"] = admin_email
        message["To"] = email
        message.set_content("reset code: " + str(reset_code))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp: 
            smtp.login(admin_email, admin_password)
            smtp.send_message(message)

        pw_code = reset_code
        return jsonify("email sent")

@app.route('/change-password', methods=['POST'])
def change_password():
    request_body = request.get_json(force = True)
    email = request_body["email"]
    user = User.query.filter_by(email = email).first()

    return jsonify(pw_code)

@app.route('/watchlist-delete', methods=['DELETE'])
def deleteStock():
    request_body = request.get_json(force=True)
    user_id = request_body["user_id"]
    stock = request_body["stock"]

    targetStock = Watchlist.query.filter_by(user_id=user_id, stock=stock).first()

    if targetStock:
        db.session.delete(targetStock)
        db.session.commit()
        return jsonify("Stock deleted succesfully."), 200
    else:
        return jsonify("There was an error."), 400

@app.route('/watchlist-add/<new_stock>', methods=['POST'])
def addStock(new_stock):
    request_body = request.get_json(force=True)
    user_id = request_body["user_id"]

    user = User.query.filter_by(id=user_id).first()
    stockExist = Watchlist.query.filter_by(user_id=user_id, stock = new_stock).first()

    if user and stockExist == None:
        newStock = Watchlist(user_id=user_id, stock=new_stock.upper(),)
        db.session.add(newStock)
        db.session.commit()
        return jsonify("New stock added."), 200
    else:    
        return jsonify("Something went wrong. Stock might exist already."), 400

@app.route('/all-watchlist', methods=['GET'])
def getAllWatchlists():
    watchlists = Watchlist.query.all()

    readWatchlists = list(map(lambda watchlist: watchlist.serialize(), watchlists))

    return jsonify(readWatchlists), 200



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
