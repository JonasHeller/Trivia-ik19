import urllib
import json
import urllib.request
import random
import html

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from helpers import *

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///trivia.db")

@app.route("/", methods=["GET", "POST"])
def index():
    '''Log in and register'''
    session.clear()
    # POST method
    if request.method == "POST":

        # Login method
        if request.form.get('submit') == "login":

            # Enuser a username was submitted
            if not request.form.get("username"):
                return apology("Doesn't input a username")

            # Ensure password was submitted
            elif not request.form.get("password"):
                return apology("Doesn't input a password")

            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

            # Ensure username exists and password is correct
            if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
                return apology("Inputs wrong account login")

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # Redirect user to home page
            return render_template("index.html")

            # Register method
        elif request.form.get("submit") == "register":

            # Is username, country, password or repeat password are missing
            if request.form["username"] == "":
                return apology("Forgets to input username")
            elif request.form["password"] == "":
                return apology("Forgets to input password")
            elif request.form["passwordagain"] == "":
                return apology("Forgets to input password again")
            elif request.form["country"] == "":
                return apology("Forgets to input country")

            # Checks if passwords are the same
            if request.form.get("passwordagain") != request.form.get("password"):
                return apology("Doesn't match his passwords")

            # Try to input user into database
            namen = db.execute("INSERT INTO users (username, hash, country) VALUES(:username, :hash, :country)", username=request.form.get("username"), hash = pwd_context.hash(request.form.get("password")), country = request.form.get("country"))
            if not namen:
                return apology("Picks a username thats already taken")

            # Remember wich user just registerd
            session['user_id'] = namen
            return render_template("index.html")

    else:
        # GET method
        return render_template("indexnot.html")


@app.route("/indexnot")
def indexnot():
    '''Log user out'''

    # Forget any user_id
    session.clear()

    if request.method == "GET":

        # Redirect user to login form
        return redirect(url_for("/"))


@app.route("/rankings", methods=["GET", "POST"])
@login_required
def ranking():
    '''Ranking'''
    # POST method
    if request.method == "POST":

        # Selects wich country the user want to see
        dataland = db.execute("SELECT * FROM users WHERE country =:country", country = request.form.get("country"))
        lijstland = []

        # Personal score
        user = db.execute("SELECT * FROM users WHERE id=:id", id=session["user_id"])

        # Country ranking
        for i in range(len(dataland)):
            mini = ()
            username = dataland[i]["username"]
            score = dataland[i]["score"]
            mini = ((score, username))
            lijstland.append(mini)

        # If there are less than ten players in a country fill the remainder of the list
        while len(lijstland) < 10:
            mini = ()
            username = "None"
            score = int(0)
            mini = ((score, username))
            lijstland.append(mini)

        # Display country's ranking
        lijstland = sorted(lijstland, reverse=True)
        return render_template("rankings.html", pscore = user[0]["score"], countryrank=request.form.get("country"), name1 = lijstland[0][1], score1 = lijstland[0][0], name2 = lijstland[1][1], score2 = lijstland[1][0], name3 = lijstland[2][1], score3 = lijstland[2][0], name4 = lijstland[3][1], score4 = lijstland[3][0], name5 = lijstland[4][1], score5 = lijstland[4][0], name6 = lijstland[5][1], score6 = lijstland[5][0], name7 = lijstland[6][1], score7 = lijstland[6][0], name8 = lijstland[7][1], score8 = lijstland[7][0], name9 = lijstland[8][1], score9 = lijstland[8][0], name10 = lijstland[9][1], score10 = lijstland[9][0])

    else:
        # GET method

        lijst = []
        info = db.execute("SELECT * FROM users")

        # Personal score
        user = db.execute("SELECT * FROM users WHERE id=:id", id=session["user_id"])
        country = user[0]["country"]
        # Counry ranking
        for i in range(len(info)):
            mini= ()
            username = info[i]["username"]
            score = info[i]["score"]
            mini = ((score, username))
            lijst.append(mini)

        # Display country's ranking
        lijst = sorted(lijst, reverse=True)
        return render_template("rankings.html", pscore = user[0]["score"], name1 = lijst[0][1], countryrank=country, score1 = lijst[0][0], name2 = lijst[1][1], score2 = lijst[1][0], name3 = lijst[2][1], score3 = lijst[2][0], name4 = lijst[3][1], score4 = lijst[3][0], name5 = lijst[4][1], score5 = lijst[4][0], name6 = lijst[5][1], score6 = lijst[5][0], name7 = lijst[6][1], score7 = lijst[6][0], name8 = lijst[7][1], score8 = lijst[7][0], name9 = lijst[8][1], score9 = lijst[8][0], name10 = lijst[9][1], score10 = lijst[9][0])


@app.route("/play", methods=["GET", "POST"])
@login_required
def play():
    '''Play'''
    # POST method
    if request.method == "POST":
        db.execute("UPDATE users SET qnumber = :qnumber WHERE id=:id",id=session["user_id"], qnumber = 0)
        db.execute("UPDATE users SET streak = :streak WHERE id=:id",id=session["user_id"], streak = 0)

        # Base link
        link = str('https://opentdb.com/api.php?amount=1&category=')

        # Category number
        category = request.form["category"]
        link += str(category)

        # Add an &
        link += str('&difficulty=')

        # Difficulty number
        difficulty = str(request.form["difficulty"])
        link += str(difficulty)

        # Selects difficulty points level
        if difficulty == 'easy':
            punten = 1
        elif difficulty == 'medium':
            punten = 2
        else:
            punten = 3
        db.execute("UPDATE users SET difficulty = :difficulty WHERE id=:id", difficulty = punten, id=session["user_id"])

        # Makes sure all questions are multiple choise
        link += str('&type=multiple')
        db.execute("UPDATE users SET url = :url WHERE id=:id", url= link, id=session["user_id"])

        return redirect(url_for("game"))

    else:
        # GET method
        return render_template("play.html")


@app.route("/game", methods=["GET", "POST"])
@login_required
def game():
    '''Game'''
    # POST method
    if request.method == "POST":
        # Keeps track how many questions where awnsered right
        streak = db.execute("SELECT streak FROM users WHERE id=:id",id=session["user_id"])
        streak = streak[0]["streak"]
        # Remember the posistion of the correct awnser
        goedantwoord = db.execute("SELECT correct FROM users WHERE id=:id",id=session["user_id"])

        # Selects difficulty score
        punten = db.execute("SELECT difficulty FROM users WHERE id=:id",id=session["user_id"])
        punten = punten[0]['difficulty']
        # Checks if given awnser is correct
        if request.form.get("option") == goedantwoord[0]['correct']:
            streak += (1 * punten)
<<<<<<< HEAD
            db.execute("UPDATE users SET streak = :streak WHERE id=:id",id=session["user_id"], streak = streak)
=======
            db.execute("UPDATE users SET streak = :streak WHERE id=:id",id=session["user_id"], streak = streak[0]['streak'])
>>>>>>> b58901e0ec1c112e18a61cb4f4e7cbc0fd198481

        return redirect(url_for("game"))

    else:
        # GET method
        keuzeantwoorden = []

        # Selects question number and url
        i = db.execute("SELECT qnumber FROM users WHERE id=:id",id=session["user_id"])
        i = i[0]['qnumber']
        url = db.execute("SELECT url FROM users WHERE id=:id",id=session["user_id"])

        # Checks if ten questions have been asked
        if i == 9:
            return redirect(url_for("end"))
        data = question(url[0]["url"])

        # Selects question and awnsers
        vraag = data["results"][0]["question"]
        vraag = html.unescape(vraag)
        foutantwoorden = data["results"][0]["incorrect_answers"]
        goedantwoord = data["results"][0]["correct_answer"]
        goedantwoord = html.unescape(goedantwoord)

        # Unescapes all special characters
        fout1 = html.unescape(foutantwoorden[0])
        fout2 = html.unescape(foutantwoorden[1])
        fout3 = html.unescape(foutantwoorden[2])

        # Adds all awnsers to a list and shuffles them
        keuzeantwoorden.append(fout1)
        keuzeantwoorden.append(fout2)
        keuzeantwoorden.append(fout3)
        keuzeantwoorden.append(goedantwoord)
        random.shuffle(keuzeantwoorden)

        # Saves the position of the correct awnser
        goedpositie = [i for i,x in enumerate(keuzeantwoorden) if x == goedantwoord]
        db.execute("UPDATE users SET correct = :correct WHERE id = :id", correct = goedpositie, id=session["user_id"])

        # Update qnumber
        i += 1
        db.execute("UPDATE users SET qnumber = :qnumber WHERE id=:id",id=session["user_id"], qnumber = i)

        return render_template("game.html", question = vraag, qnumber = i, option_one = keuzeantwoorden[0], option_two = keuzeantwoorden[1], option_three = keuzeantwoorden[2], option_four = keuzeantwoorden[3])


@app.route("/index", methods=["GET","POST"])
@login_required
def indexroute():
    '''Index'''
    return render_template("index.html")


@app.route("/endpage", methods=["GET","POST"])
@login_required
def end():
    '''Endpage'''
    # POST method
    if request.method == "POST":
        return render_template("endpage.html")

    else:
        # GET method

        # Displays the points gotten
        streak = db.execute("SELECT streak FROM users WHERE id=:id",id=session["user_id"])
        streak = streak[0]['streak']

        # Updates total points
        score = db.execute("SELECT score FROM users WHERE id=:id", id=session["user_id"])
        score = score[0]["score"]
        score += streak
        db.execute("UPDATE users SET score = :score WHERE id =:id", id=session["user_id"], score = score)
        return render_template("endpage.html", pscore=streak)


@app.route("/profile", methods=["GET","POST"])
@login_required
def profile():
    '''See user profile'''
    # POST method
    if request.method == "POST":

        # Change country
        if request.form.get('submit') == "update2":

            # New country
            newcountry = request.form.get("country")

            # Confirming if the old country is correct
            country = db.execute("SELECT country FROM users WHERE id = :id", id=session['user_id'])

            # Updating the users table's country
            if country[0]["country"] != newcountry:
                db.execute("UPDATE users SET country = :country WHERE id=:id", country=newcountry, id=session["user_id"])
                flash("Country changed succesfully!")
                return render_template("index.html")

        # Change password
        elif request.form.get("submit") == "update1":

            # If password, new password or repeat password are missing
            if request.form["password"] == "":
                return apology("Forgets to input password")
            elif request.form["passwordagain"] == "":
                return apology("Forgets to input password again")
            elif request.form["newpassword"] == "":
                return apology("Forgets to input a new password")

            # Checks if passwords are the same
            if request.form.get("passwordagain") != request.form.get("newpassword"):
                return apology("Doesn't match his passwords")

            # Update users password
            db.execute("UPDATE users SET hash = :hash WHERE id = :id",hash = pwd_context.hash(request.form.get("newpassword")), id=session["user_id"])
            return render_template("index.html")

    else:
        # GET method
        return render_template("profile.html")

