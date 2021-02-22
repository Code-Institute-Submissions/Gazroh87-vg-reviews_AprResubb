import os
from flask import (
    Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
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
    platforms = list(mongo.db.platforms.find().sort("platform", 1))
    return render_template("home.html", platforms=platforms)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    reviews = list(mongo.db.reviews.find({"$text": {"$search": query}}))
    return render_template("reviews.html", reviews=reviews)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Account Registered!")
        return redirect(url_for("account", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "account", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/account/<username>", methods=["GET", "POST"])
def account(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("account.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You are now logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/get_reviews")
def get_reviews():
    reviews = mongo.db.reviews.find().sort("_id", -1)
    return render_template("reviews.html", reviews=reviews)


@app.route("/add_review", methods=["GET", "POST"])
def add_review():
    if request.method == "POST":
        review = {
            "title": request.form.get("title"),
            "platform": request.form.get("platform"),
            "review": request.form.get("review"),
            "completed": request.form.get("completed"),
            "reviewed_by": session["user"]
        }
        mongo.db.reviews.insert_one(review)
        flash("Review Added Successfully!")
        return redirect(url_for("get_reviews"))

    games = mongo.db.games.find().sort("title", 1)
    platforms = mongo.db.platforms.find().sort("platform", 1)
    return render_template(
        "add_review.html", games=games, platforms=platforms)


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    if request.method == "POST":
        submit = {
            "title": request.form.get("title"),
            "platform": request.form.get("platform"),
            "review": request.form.get("review"),
            "completed": request.form.get("completed"),
            "reviewed_by": session["user"]
        }
        mongo.db.reviews.update({"_id": ObjectId(review_id)}, submit)
        flash("Review Changes Saved!")
        return redirect(url_for("my_reviews"))

    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    games = mongo.db.games.find().sort("title", 1)
    platforms = mongo.db.platforms.find().sort("platform", 1)
    return render_template("edit_review.html",
                           review=review,
                           games=games,
                           platforms=platforms)


@app.route("/delete_review/<review_id>")
def delete_review(review_id):
    mongo.db.reviews.remove({"_id": ObjectId(review_id)})
    flash("Review Deleted Successfully")
    return redirect(url_for("get_reviews"))


@app.route("/my_reviews")
def my_reviews():
    reviews = list(mongo.db.reviews.find(
        {"created_by": session["user"]}).sort("_id", -1))
    return render_template("my_reviews.html", reviews=reviews)


@app.route("/get_games")
def get_games():
    games = list(mongo.db.games.find().sort("title", 1))
    return render_template("games.html", games=games)


@app.route("/add_game", methods=["GET", "POST"])
def add_game():
    if request.method == "POST":
        game = {
            "title": request.form.get("title")
        }
        mongo.db.games.insert_one(game)
        flash("Game Added Successfully!")
        return redirect(url_for("get_games"))

    return render_template("add_game.html")


@app.route("/edit_game/<game_id>", methods=["GET", "POST"])
def edit_game(game_id):
    if request.method == "POST":
        submit = {
            "title": request.form.get("title")
        }
        mongo.db.games.update({"_id": ObjectId(game_id)}, submit)
        flash("Game Changes Saved!")
        return redirect(url_for("get_games"))


@app.route("/delete_game/<game_id>")
def delete_game(game_id):
    mongo.db.geames.remove({"_id": ObjectId(game_id)})
    flash("Game Deleted Successfully")
    return redirect(url_for("get_games"))


@app.route("/get_genres")
def get_genres():
    genres = list(mongo.db.genres.find().sort("genre", 1))
    return render_template("genres.html", genres=genres)


@app.route("/get_platforms")
def get_platforms():
    platforms = list(mongo.db.platforms.find().sort("platform", 1))
    return render_template("platforms.html", platforms=platforms)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
