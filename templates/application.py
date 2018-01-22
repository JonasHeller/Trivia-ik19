import urllib
import json
import urllib.request

keuzeantwoorden = []


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
        elif request.form["password_confirmation"] == "":
            return apology("Missing repeat password!")
        elif request.form["country"] == "":
            return apology("Missing country!")

        # Spelling gelijk maken voor alle landen, kleine letters
        country = request.form["country"]

        # Controle of het wachtwoord overeenkomt
        elif request.form["password_confirmation"] != request.form["password"]:
             return apology("Password and repeated password are not equal")

        # zoeken naar naam en als het al bestaat, moet dit vermeld worden
        info = db.execute("INSERT INTO users (username, hash, country) VALUES(:username, :hash, :country)",
        username=request.form.get("username"), hash = pwd_context.hash(request.form.get("password"), country=country))
        if not namen:
            return apology("Username taken!")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("Invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

        # GET methode
    else:
        return render_template("register.html")
    return

    return apology("WELKOM!")


@app.route("/password", methods=["GET", "POST"])
def password():
    '''Wachtwoord veranderen'''
    # POST methode
    if request.method == "POST":

        # missing information
        if not request.form.get("oldpassword"):
            return apology("must enter old password")
        elif not request.for.get("new_password"):
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
        elif not request.for.get("new_country"):
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
def ranking():
    '''Ranking'''
    # POST methode
    if request.method == "POST":

        def wereldranking():
            db.execute("SELECT * FROM users ORDER BY DESC;

                        WITH  Result AS
                        (
                        SELECT points,
                        DENSE_RANK() OVER (ORDER BY points DESC) AS Score_rank
                        FROM users
                        )
                        SELECT TOP 10 points FROM Result")

        def eigenranking():
            id = session["user_id"]
            db.execute("SELECT * FROM users ORDER BY DESC;

                        WITH  Result AS
                        (
                        SELECT points,
                        DENSE_RANK() OVER (ORDER BY points DESC) AS Score_rank
                        FROM users
                        )
                        SELECT TOP 1 points FROM Result WHERE id=:id")

        def landranking():
            db.execute("SELECT * FROM users ORDER BY DESC;

                        WITH  Result AS
                        (
                        SELECT points,
                        DENSE_RANK() OVER (ORDER BY points DESC) AS Score_rank
                        FROM users
                        )
                        SELECT TOP 10 points FROM Result WHERE country=request.form.get("country")")

    else:
        # GET methode
        return render_template("ranking.html")


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

        if difficulty = 'easy':
            punten = 1
        elif difficulty = 'medium':
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
        if TODO = goedantwoord:
            TODO # WILLEN TOTALE PUNTEN SCORE UPDATEN OF SCOREN VAN VRAGEN ALLEEN?
            score += punten
            return GOED
        else:
            return FOUT

    else:
        # GET methode
        return render_template("play.html")