import os
from flask import (
    Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    genres = mongo.db.genres.find()
    # return "Flask is working" + str(mongo.db.genres.find_one())
    return render_template("home.html", genres=genres)


@app.route("/get_reviews")
def get_reviews():
    reviews = mongo.db.reviews.find()
    return render_template("reviews.html", reviews=reviews)


@app.route("/get_games")
def get_games():
    return render_template("games.html", games=games)


@app.route("/get_genres")
def get_genres():
    return render_template("genres.html", genres=genres)


@app.route("/get_platforms")
def get_platforms():
    return render_template("platforms.html", platforms=platforms)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            # Update debug=False to True before deployment or submission.
            debug=True)
