import urllib
import json
import urllib.request

keuzeantwoorden = []

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///trivia.db")

@app.route("/")
def index():
    return render_template("indexnot.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # clear login
    session.clear()

    # POST methode
    if request.method == "POST":

    # Als username, password of repeat password mist
        if request.form["username"] == "":
            return apology("Missing username!")
        elif request.form["password"] == "":
            return apology("Missing password!")
        elif request.form["passwordagain"] == "":
            return apology("Missing repeat password!")
        elif request.form["country"] == "":
            return apology("Missing country!")

        # Spelling gelijk maken voor alle landen, kleine letters
        country = request.form["country"]

        # Controle of het wachtwoord overeenkomt
        if request.form.get("passwordagain") != request.form.get("password"):
             return apology("Password and repeated password are not equal")


        namen = db.execute("INSERT INTO users (username, hash, country) VALUES(:username, :hash, :country)", username=request.form.get("username"), hash = pwd_context.hash(request.form.get("password")), country = request.form.get("country"))

        if not namen:
            return apology("Username taken!")

        session['user_id'] = namen

        return render_template("index.html")


    else:
        return render_template("indexnot.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return render_template("index.html")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("indexnot.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/password", methods=["GET", "POST"])
def password():
    '''Wachtwoord veranderen'''
    # POST methode
    if request.method == "POST":

        # missing information
        if not request.form.get("old_password"):
            return apology("must enter old password")
        elif not request.form.get("new_password"):
            return apology("must enter new password")
        elif not request.form.get("confirmation"):
            return apology("must enter new password again")

        # confirming the password and password again
        if request.form.get("confirmation") != request.form.get("new"):
            return apology("passwords did not match")

        # confirming if the old password is correct
        hashes = db.execute("SELECT hash FROM users WHERE id = :id", id=session['user_id'])
        if not pwd_context.verify(request.form.get("old_password"), hashes[0]["hash"]):
            return apology("old password is wrong")

        # updating the users table's hash
        db.execute("UPDATE users SET hash = :hash WHERE id=:id", hash=pwd_context.hash(request.form.get("new_password")), id=session["user_id"])
        flash("Password changed succesfully!")
        return redirect(url_for("index"))

    else:
        # GET methode
        return render_template("password.html")


app.route("/country", methods=["GET", "POST"])
def country():
    '''Country veranderen'''
    # POST methode
    if request.method == "POST":

        # missing information
        if not request.form.get("old_country"):
            return apology("must enter old country")
        elif not request.form.get("new_country"):
            return apology("must enter new country")
        elif not request.form.get("confirmation"):
            return apology("must enter new country again")

        # confirming the country and country again
        if request.form.get("confirmation") != request.form.get("new_country"):
            return apology("countries did not match")

        # confirming if the old country is correct
        country = db.execute("SELECT country FROM users WHERE id = :id", id=session['user_id'])
        if request.form.get("old_country") != country:
            return apology("old country is wrong")

        # updating the users table's country
        db.execute("UPDATE users SET country = :country WHERE id=:id", country=request.form.get("new_country"), id=session["user_id"])
        flash("Country changed succesfully!")
        return redirect(url_for("index"))

    else:
        # GET methode
        return render_template("country.html")


app.route("/ranking", methods=["GET", "POST"])
#def ranking():
#    '''Ranking'''
#    # POST methode
#    if request.method == "POST":

#        def wereldranking():
#            db.execute("SELECT * FROM users ORDER BY DESC;
#
#                        WITH  Result AS
#                        (
#                        SELECT points,
#                        DENSE_RANK() OVER (ORDER BY points DESC) AS Score_rank
#                        FROM users
#                        )
#                        SELECT TOP 10 points FROM Result")
#
#        def eigenranking():
#            id = session["user_id"]
#            db.execute("SELECT * FROM users ORDER BY DESC;

#                        WITH  Result AS
#                        (
#                        SELECT points,
#                        DENSE_RANK() OVER (ORDER BY points DESC) AS Score_rank
#                        FROM users
#                        )
#                        SELECT TOP 1 points FROM Result WHERE id=:id")

#        def landranking():
#            db.execute("SELECT * FROM users ORDER BY DESC;

#                        WITH  Result AS
#                        (
#                        SELECT points,
#                        DENSE_RANK() OVER (ORDER BY points DESC) AS Score_rank
#                        FROM users
#                        )
#                        SELECT TOP 10 points FROM Result WHERE country=request.form.get("country")")
#
#    else:
#        # GET methode
#        return render_template("ranking.html")


app.route("/play", methods=["GET", "POST"])
def play():
    '''Play'''
    # POST methode
    if request.method == "POST":

        score = 0

        # als er iets mist
        if request.form["categorie"] == "":
            return apology("Missing categorie!")
        elif request.form["difficulty"] == "":
            return apology("Missing difficulty!")

        # voorbeeld URL: https://opentdb.com/api.php?amount=10&category=9&difficulty=easy&type=multiple
        url = str('https://opentdb.com/api.php?amount=10&category=')

        # categorie nummer maken
        categorie = request.form["categorie"]
        # TODO van categorie naar nummer
        url += str(categorie)

        # & toevoegen
        url += str('&difficulty=')

        # difficulty nummer maken
        difficulty = str(request.form["difficulty"])
        url += str(difficulty)

        if difficulty == 'easy':
            punten = 1
        elif difficulty == 'medium':
            punten = 2
        else:
            punten = 3

        # laatste deel toevoegen '&type=multiple)'
        url += str('&type=multiple')

        # de vragen opvragen uit de API
        json_obj = urllib.request.urlopen(url).read()
        response = urllib.request.urlopen(url).read()
        json_obj = str(response, 'utf-8')
        data = json.loads(json_obj)

    else:
        # GET methode
        return render_template("play.html")


app.route("/question", methods=["GET", "POST"])
def question():
    '''question'''
    # POST methode
    if request.method == "POST":

        # initialize, vraag i
        vraag = data["results"][i]["question"]
        foutantwoorden = data["results"][i]["incorrect_answers"]
        goedantwoord = data["results"][i]["correct_answer"]

        # antwoorden shufflen, keuzeantwoorden is een lijst
        keuzeantwoorden.append(foutantwoorden)
        keuzeantwoorden.append(goedantwoord)
        random.shuffle(keuzeantwoorden)

        # of antwoord goed is
        #if TODO = goedantwoord:
        #    TODO # WILLEN TOTALE PUNTEN SCORE UPDATEN OF SCOREN VAN VRAGEN ALLEEN?
        #    score += punten
        #    return GOED
        #else:
        #    return FOUT

    else:
        # GET methode
        return render_template("play.html")