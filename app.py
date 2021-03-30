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


# Landing/homepage function
@app.route("/")
@app.route("/home")
def home():
    """
    Finds all platforms in the db and sorts them in a list by name,
    alphabetically to display them in a carousel
    """
    platforms = list(mongo.db.platforms.find().sort("platform", 1))
    return render_template("home.html", platforms=platforms)


# Search functionality
@app.route("/search_reviews", methods=["GET", "POST"])
def search_reviews():
    """
    Performs a text index search on the reviews collection using the
    query variable
    """
    query = request.form.get("query")
    reviews = list(mongo.db.reviews.find({"$text": {"$search": query}}))
    return render_template("reviews.html", reviews=reviews)


@app.route("/search_games", methods=["GET", "POST"])
def search_games():
    """
    Performs a text index search on the games collection using the
    query variable
    """
    query = request.form.get("query-games")
    games = list(mongo.db.games.find({"$text": {"$search": query}}))
    return render_template("games.html", games=games)


# Account registration function
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


# Login functionality
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
    """grab the session user's username from db"""
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("account.html", username=username)

    return redirect(url_for("login"))


# Logout function
@app.route("/logout")
def logout():
    """remove user from session cookies"""
    flash("You are now logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/get_reviews")
def get_reviews():
    """
    Finds all reviews in db and sorts them chronologically
    with the most recent reviews displayed first based on
    datetime info stored in the id
    """
    reviews = list(mongo.db.reviews.find().sort("_id", -1))
    return render_template("reviews.html", reviews=reviews)


@app.route("/add_review", methods=["GET", "POST"])
def add_review():
    """
    Creates dictionary for form and inserts user inputs
    into db
    """
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

    # Finds games and platforms in db and sorts them alphabetically
    games = mongo.db.games.find().sort("title", 1)
    platforms = mongo.db.platforms.find().sort("platform", 1)
    return render_template(
        "add_review.html", games=games, platforms=platforms)


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    """
    Finds review by id and db is updated with user form input
    """
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
    """
    Finds review by id and removes it from db
    """
    mongo.db.reviews.remove({"_id": ObjectId(review_id)})
    flash("Review Deleted Successfully")
    return redirect(url_for("get_reviews"))


@app.route("/my_reviews")
def my_reviews():
    """
    Finds reviews created by the session user
    and sorts them by most recent
    """
    reviews = list(mongo.db.reviews.find(
        {"created_by": session["user"]}).sort("_id", -1))
    return render_template("my_reviews.html", reviews=reviews)


@app.route("/get_games")
def get_games():
    """
    Finds all games in db and sorts them alphabetically
    by title
    """
    games = list(mongo.db.games.find().sort("title", 1))
    return render_template("games.html", games=games)


@app.route("/add_game", methods=["GET", "POST"])
def add_game():
    """
    Creates dictionary for form and inserts user inputted
    new game into db
    """
    if request.method == "POST":
        game = {
            "title": request.form.get("title"),
            "img_url": request.form.get("img_url"),
            "description": request.form.get("description"),
            "genre": request.form.get("genre"),
            "developer": request.form.get("developer"),
            "platform": request.form.get("platform"),
            "year": request.form.get("year"),
            "added_by": session["user"]
        }
        mongo.db.games.insert_one(game)
        flash("Game Added Successfully!")
        return redirect(url_for("get_games"))

    genres = mongo.db.genres.find().sort("genre", 1)
    platforms = mongo.db.platforms.find().sort("platform", 1)
    return render_template("add_game.html", genres=genres, platforms=platforms)


@app.route("/edit_game/<game_id>", methods=["GET", "POST"])
def edit_game(game_id):
    """
    Finds game by id and db is updated with user form input
    """
    if request.method == "POST":
        submit = {
            "title": request.form.get("title"),
            "img_url": request.form.get("img_url"),
            "description": request.form.get("description"),
            "genre": request.form.get("genre"),
            "developer": request.form.get("developer"),
            "platform": request.form.get("platform"),
            "year": request.form.get("year"),
            "added_by": session.get["user"]
        }
        mongo.db.games.update({"_id": ObjectId(game_id)}, submit)
        flash("Game Changes Saved!")
        return redirect(url_for("get_games"))


@app.route("/delete_game/<game_id>")
def delete_game(game_id):
    """
    Finds game by id and removes it from db
    """
    mongo.db.games.remove({"_id": ObjectId(game_id)})
    flash("Game Deleted Successfully")
    return redirect(url_for("get_games"))


@app.route("/find_game/<title>", methods=["GET", "POST"])
def find_game(title):
    """
    Returns a list of reviews that contain the specific game name
    """
    reviews = list(mongo.db.reviews.find({"title": title}))
    return render_template("reviews.html", reviews=reviews)


@app.route("/get_genres")
def get_genres():
    """
    Finds all genres in db and sorts them alphabetically
    by name
    """
    genres = list(mongo.db.genres.find().sort("genre", 1))
    return render_template("genres.html", genres=genres)


@app.route("/add_genre", methods=["GET", "POST"])
def add_genre():
    """
    Creates dictionary for form and inserts user inputted
    new genre into db
    """
    if request.method == "POST":
        genre = {
            "genre": request.form.get("genre")
        }
        mongo.db.genres.insert_one(genre)
        flash("Genre Added Successfully!")
        return redirect(url_for("get_genres"))

    return render_template("add_genre.html")


@app.route("/edit_genre/<genre_id>", methods=["GET", "POST"])
def edit_genre(genre_id):
    """
    Finds genre by id and db is updated with user form input
    """
    if request.method == "POST":
        submit = {
            "genre": request.form.get("genre")
        }
        mongo.db.genres.update({"_id": ObjectId(genre_id)}, submit)
        flash("Genre Changes Successfully!")
        return redirect(url_for("get_genres"))


@app.route("/delete_genre/<genre_id>")
def delete_genre(genre_id):
    """
    Finds genre by id and removes it from db
    """
    mongo.db.genres.remove({"_id": ObjectId(genre_id)})
    flash("Genre Deleted Successfully")
    return redirect(url_for("get_genres"))


@app.route("/get_platforms")
def get_platforms():
    """
    Finds all platforms in db and sorts them alphabetically
    by name
    """
    platforms = list(mongo.db.platforms.find().sort("platform", 1))
    return render_template("platforms.html", platforms=platforms)


@app.route("/add_platform", methods=["GET", "POST"])
def add_platform():
    """
    Creates dictionary for form and inserts user inputted
    new platform into db
    """
    if request.method == "POST":
        platform = {
            "platform": request.form.get("platform"),
            "img_url": request.form.get("img_url")
        }
        mongo.db.platforms.insert_one(platform)
        flash("Platform Added Successfully!")
        return redirect(url_for("get_platforms"))

    return render_template("add_platform.html")


@app.route("/edit_platform/<platform_id>", methods=["GET", "POST"])
def edit_platform(platform_id):
    """
    Finds platform by id and db is updated with user form input
    """
    if request.method == "POST":
        submit = {
            "platform": request.form.get("platform"),
            "img_url": request.form.get("img_url")
        }
        mongo.db.platforms.update({"_id": ObjectId(platform_id)}, submit)
        flash("Platform Edited Successfully!")
        return redirect(url_for("get_platforms"))


@app.route("/delete_platform/<platform_id>")
def delete_platform(platform_id):
    """
    Finds platform by id and removes it from db
    """
    mongo.db.platforms.remove({"_id": ObjectId(platform_id)})
    flash("Genre Deleted Successfully")
    return redirect(url_for("get_platforms"))


@app.route("/find_platform/<platform>", methods=["GET", "POST"])
def find_platform(platform):
    """
    Returns a list of reviews that contain the specific platform name
    """
    reviews = list(mongo.db.reviews.find({"platform": platform}))
    return render_template("reviews.html", reviews=reviews)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
