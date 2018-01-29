import urllib
import json
import urllib.request
import random

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

@app.route("/", methods=["GET", "POST"])
def index():
    session.clear()
    if request.method == "POST":
        if request.form.get('submit') == "login":
            if not request.form.get("username"):
                return apology("Doesn't input a username")

            # ensure password was submitted
            elif not request.form.get("password"):
                return apology("Doesn't input a password")

            # query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

            # ensure username exists and password is correct
            if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
                return apology("Makes an error code 400 appear")

            # remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # redirect user to home page
            return render_template("index.html")
        elif request.form.get("submit") == "register":
            # Als username, password of repeat password mist
            if request.form["username"] == "":
                return apology("Forgets to input username")
            elif request.form["password"] == "":
                return apology("Forgets to input password")
            elif request.form["passwordagain"] == "":
                return apology("Forgets to input password again")
            elif request.form["country"] == "":
                return apology("Forgets to input country")

             # Spelling gelijk maken voor alle landen, kleine letters
            country = request.form["country"]

            # Controle of het wachtwoord overeenkomt
            if request.form.get("passwordagain") != request.form.get("password"):
                return apology("Doesn't match his passwords")


            namen = db.execute("INSERT INTO users (username, hash, country) VALUES(:username, :hash, :country)", username=request.form.get("username"), hash = pwd_context.hash(request.form.get("password")), country = request.form.get("country"))
            print (namen)
            if not namen:
                return apology("Picks a username thats already taken")

            session['user_id'] = namen

            return render_template("index.html")

    else:
        return render_template("indexnot.html")


@app.route("/indexnot")
def indexnot():
    """Log user out."""

    # forget any user_id
    session.clear()

    if request.method == "GET":
        # redirect user to login form
        return redirect(url_for("/"))

@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    '''Wachtwoord veranderen'''
    # POST methode
    if request.method == "POST":

        # missing information
        if not request.form.get("old_password"):
            return apology("Doesn't enter his old password")
        elif not request.form.get("new_password"):
            return apology("Doesn't enter his new password")
        elif not request.form.get("confirmation"):
            return apology("Doesn't enter his new password again")

        # confirming the password and password again
        if request.form.get("confirmation") != request.form.get("new"):
            return apology("Doesn't match his passwords")

        # confirming if the old password is correct
        hashes = db.execute("SELECT hash FROM users WHERE id = :id", id=session['user_id'])
        if not pwd_context.verify(request.form.get("old_password"), hashes[0]["hash"]):
            return apology("Inputs wrong password")

        # updating the users table's hash
        db.execute("UPDATE users SET hash = :hash WHERE id=:id", hash=pwd_context.hash(request.form.get("new_password")), id=session["user_id"])
        flash("Password changed succesfully!")
        return redirect(url_for("index"))

    else:
        # GET methode
        return render_template("password.html")


@app.route("/country", methods=["GET", "POST"])
@login_required
def country():
    '''Country veranderen'''
    # POST methode
    if request.method == "POST":

        # missing information
        if not request.form.get("old_country"):
            return apology("Forgets to input his old country")
        elif not request.form.get("new_country"):
            return apology("Forgets to input his new country")
        elif not request.form.get("confirmation"):
            return apology("Forgets to input his new country twice")

        # confirming the country and country again
        if request.form.get("confirmation") != request.form.get("new_country"):
            return apology("Doesn't match his countries")

        # confirming if the old country is correct
        country = db.execute("SELECT country FROM users WHERE id = :id", id=session['user_id'])
        if request.form.get("old_country") != country:
            return apology("Doesn't remember which country he lives in")

        # updating the users table's country
        db.execute("UPDATE users SET country = :country WHERE id=:id", country=request.form.get("new_country"), id=session["user_id"])
        flash("Country changed succesfully!")
        return redirect(url_for("index"))

    else:
        # GET methode
        return render_template("country.html")


@app.route("/rankings", methods=["GET", "POST"])
@login_required
def ranking():
    '''Ranking'''
    # POST methode
    if request.method == "POST":
        landkeuze = request.form.get("country")
        print(landkeuze)
        dataland = db.execute("SELECT * FROM users WHERE country =:country", country = landkeuze)
        print(dataland)
        lijstland = []

        # persoonlijke score
        user = db.execute("SELECT * FROM users WHERE id=:id", id=session["user_id"])
        pscore = user[0]["score"]

        # wereldranking
        for i in range(len(dataland)):
            mini = ()
            username = dataland[i]["username"]
            score = dataland[i]["score"]
            mini = ((score, username))
            lijstland.append(mini)

        while len(lijstland) < 10:
            mini = ()
            username = "None"
            score = int(0)
            mini = ((score, username))
            lijstland.append(mini)

        print(lijstland)

        lijstland = sorted(lijstland, reverse=True)
        return render_template("rankings.html", pscore = pscore, name1 = lijstland[0][1], score1 = lijstland[0][0], name2 = lijstland[1][1], score2 = lijstland[1][0], name3 = lijstland[2][1], score3 = lijstland[2][0], name4 = lijstland[3][1], score4 = lijstland[3][0], name5 = lijstland[4][1], score5 = lijstland[4][0], name6 = lijstland[5][1], score6 = lijstland[5][0], name7 = lijstland[6][1], score7 = lijstland[6][0], name8 = lijstland[7][1], score8 = lijstland[7][0], name9 = lijstland[8][1], score9 = lijstland[8][0], name10 = lijstland[9][1], score10 = lijstland[9][0])

    else:
        lijst = []
        info = db.execute("SELECT * FROM users")

        # persoonlijke score
        user = db.execute("SELECT * FROM users WHERE id=:id", id=session["user_id"])
        pscore = user[0]["score"]

        # wereldranking
        for i in range(len(info)):
            mini= ()
            username = info[i]["username"]
            score = info[i]["score"]
            mini = ((score, username))
            lijst.append(mini)

        lijst = sorted(lijst, reverse=True)

            # GET methode
        return render_template("rankings.html", pscore = pscore, name1 = lijst[0][1], score1 = lijst[0][0], name2 = lijst[1][1], score2 = lijst[1][0], name3 = lijst[2][1], score3 = lijst[2][0], name4 = lijst[3][1], score4 = lijst[3][0], name5 = lijst[4][1], score5 = lijst[4][0], name6 = lijst[5][1], score6 = lijst[5][0], name7 = lijst[6][1], score7 = lijst[6][0], name8 = lijst[7][1], score8 = lijst[7][0], name9 = lijst[8][1], score9 = lijst[8][0], name10 = lijst[9][1], score10 = lijst[9][0])
@app.route("/play", methods=["GET", "POST"])
@login_required
def play():
    '''Play'''
    # POST methode
    if request.method == "POST":
        db.execute("UPDATE users SET qnumber = :qnumber WHERE id=:id",id=session["user_id"], qnumber = 0)
        db.execute("UPDATE users SET streak = :streak WHERE id=:id",id=session["user_id"], streak = 0)

        # voorbeeld URL: https://opentdb.com/api.php?amount=10&category=9&difficulty=easy&type=multiple
        link = str('https://opentdb.com/api.php?amount=1&category=')

        # categorie nummer maken
        category = request.form["category"]
        # TODO van categorie naar nummer
        link += str(category)

        # & toevoegen
        link += str('&difficulty=')

        # difficulty nummer maken
        difficulty = str(request.form["difficulty"])
        link += str(difficulty)

        if difficulty == 'easy':
            punten = 1
        elif difficulty == 'medium':
            punten = 2
        else:
            punten = 3
        db.execute("UPDATE users SET difficulty = :difficulty WHERE id=:id", difficulty = punten, id=session["user_id"])
        # laatste deel toevoegen '&type=multiple)'
        link += str('&type=multiple')
        print(link)
        db.execute("UPDATE users SET url = :url WHERE id=:id", url= link, id=session["user_id"])

        return redirect(url_for("game"))

    else:
        # GET methode
        return render_template("play.html")


@app.route("/game", methods=["GET", "POST"])
@login_required
def game():
    '''game'''
    # POST methode
    if request.method == "POST":

        streak = db.execute("SELECT streak FROM users WHERE id=:id",id=session["user_id"])
        streak = streak[0]['streak']

        # goede antwoordpositie eruit halen
        goedantwoord = db.execute("SELECT correct FROM users WHERE id=:id",id=session["user_id"])
        goedantwoord = goedantwoord[0]['correct']

        punten = db.execute("SELECT difficulty FROM users WHERE id=:id",id=session["user_id"])
        punten = punten[0]['difficulty']
        # of antwoord goed is
        if request.form.get("option") == goedantwoord:
            streak += (1 * punten)
            db.execute("UPDATE users SET streak = :streak WHERE id=:id",id=session["user_id"], streak = streak)
            print("goed")

        # score += punten
        else:
            print("fout")

        return redirect(url_for("game"))

    else:
        # GET methode
        keuzeantwoorden = []

        # initialize, vraag i
        i = db.execute("SELECT qnumber FROM users WHERE id=:id",id=session["user_id"])
        i = i[0]['qnumber']
        url = db.execute("SELECT url FROM users WHERE id=:id",id=session["user_id"])

        #db.execute("SELECT qnumber FROM users WHERE id=:id",id=session["user_id"])
        if i == 9:
            return redirect(url_for("end"))
        data = question(url[0]["url"])

        vraag = data["results"][0]["question"]

        foutantwoorden = data["results"][0]["incorrect_answers"]
        goedantwoord = data["results"][0]["correct_answer"]

        # antwoorden shufflen, keuzeantwoorden is een lijst
        keuzeantwoorden.append(foutantwoorden[0])
        keuzeantwoorden.append(foutantwoorden[1])
        keuzeantwoorden.append(foutantwoorden[2])
        keuzeantwoorden.append(goedantwoord)
        random.shuffle(keuzeantwoorden)

        # goede positie in de lijst als antwoord
        goedpositie = [i for i,x in enumerate(keuzeantwoorden) if x == goedantwoord]
        db.execute("UPDATE users SET correct = :correct WHERE id = :id", correct = goedpositie, id=session["user_id"])

        # update qnumber
        i += 1

        db.execute("UPDATE users SET qnumber = :qnumber WHERE id=:id",id=session["user_id"], qnumber = i)

        return render_template("game.html", question = vraag, qnumber = i, option_one = keuzeantwoorden[0], option_two = keuzeantwoorden[1], option_three = keuzeantwoorden[2], option_four = keuzeantwoorden[3])

@app.route("/index", methods=["GET","POST"])
@login_required
def indexroute():
    return render_template("index.html")

@app.route("/endpage", methods=["GET","POST"])
@login_required
def end():

    if request.method == "POST":
        return render_template("endpage.html")

    else:
        streak = db.execute("SELECT streak FROM users WHERE id=:id",id=session["user_id"])
        streak = streak[0]['streak']
        score = db.execute("SELECT score FROM users WHERE id=:id", id=session["user_id"])
        score = score[0]["score"]
        score += streak
        db.execute("UPDATE users SET score = :score WHERE id =:id", id=session["user_id"], score = score)
        return render_template("endpage.html", streak=streak)