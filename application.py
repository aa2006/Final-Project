import os

import sqlalchemy
from cs50 import SQL
from flask import Flask, render_template, flash, jsonify, redirect, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from functions import login_required, apology, loggedapology

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
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

# Configure CS50 Library to use PostgreSQL database
db = SQL("I can't show you my URI!!")


# Homepage
@app.route("/")
def index():
    return render_template("index.html")

# Watch Videos (Login Required)
@app.route("/videos")
@login_required
def videos():
    id = session["user_id"]
    fname = db.execute("SELECT fname FROM users WHERE id = :id", id=id)[0]["fname"]
    lname = db.execute("SELECT lname FROM users WHERE id = :id", id=id)[0]["lname"]
    return render_template("videos.html", fname=fname, lname=lname)

# Read Articles (Login Required)
@app.route("/articles")
@login_required
def articles():
    id=session["user_id"]
    fname = db.execute("SELECT fname FROM users WHERE id = :id", id=id)[0]["fname"]
    lname = db.execute("SELECT lname FROM users WHERE id = :id", id=id)[0]["lname"]
    return render_template("articles.html", fname=fname, lname=lname)

# Solve Labs (Login Required)
@app.route("/labs")
@login_required
def labs():
    id = session["user_id"]
    fname = db.execute("SELECT fname FROM users WHERE id = :id", id=id)[0]["fname"]
    lname = db.execute("SELECT lname FROM users WHERE id = :id", id=id)[0]["lname"]
    return render_template("labs.html", fname=fname, lname=lname)

# User Dashboard (Login Required)
@app.route("/home")
@login_required
def home():
    id = session["user_id"]
    fname = db.execute("SELECT fname FROM users WHERE id = :id;", id=id)[0]["fname"]
    lname = db.execute("SELECT lname FROM users WHERE id = :id;", id=id)[0]["lname"]
    return render_template("home.html", fname=fname, lname=lname)

# First Lab (Login Required to Solve)
@app.route("/labs/easy", methods=["GET", "POST"])
@login_required
def labsEasy():
    if request.method == "GET":
        id=session["user_id"]
        fname = db.execute("SELECT fname FROM users WHERE id = :id", id=id)[0]["fname"]
        lname = db.execute("SELECT lname FROM users WHERE id = :id", id=id)[0]["lname"]
        return render_template("labsEasy.html", fname=fname, lname=lname)
    else:
        id=session["user_id"]
        problem_name = "easy"
        rows = db.execute("SELECT * FROM problems WHERE user_id = :id AND problem_name = :name", id=id, name=problem_name)
        if len(rows) == 0:
            submission = request.form.get("submission")
            text = 'Hello World! Welcome to Encryption.com!'
            if text == submission:
                id = session["user_id"]
                points = int(db.execute("SELECT points FROM users WHERE id = :id", id=id)[0]["points"])
                problems = int(db.execute("SELECT problems FROM users WHERE id = :id", id=id)[0]["problems"])
                db.execute("UPDATE users SET points = :points, problems = :problems WHERE id = :id", points=(points+5), problems=(problems+1), id=id)
                db.execute("INSERT INTO problems(user_id, problem_name, points) VALUES (:id, :name, :points);", id=id, name=problem_name, points=5)
                return redirect("/leaderboard")
            else:
                return redirect("/labs/easy")
        else:
            return redirect("/labs")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("Invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]
        return redirect("/home")
    else:
        return render_template("login.html")

# Leaderboard (Login required to view)
@app.route("/leaderboard")
@login_required
def leaderboard():
    id = session["user_id"]
    fname = db.execute("SELECT fname FROM users WHERE id = :id", id=id)[0]["fname"]
    lname = db.execute("SELECT lname FROM users WHERE id = :id", id=id)[0]["lname"]
    rows = db.execute("SELECT id, fname, username, problems, points FROM users ORDER BY points DESC LIMIT 500;")
    pos = 0
    return render_template("leaderboard.html", fname=fname, lname=lname, rows=rows, pos=pos)

# Sign up page
@app.route("/register", methods=["GET", "POST"])
def register():
    #clear all user data
    session.clear()

    if request.method == "POST":
        if request.form.get("pwd") != request.form.get("confirmation"):
            return apology("The passwords do not match", 403)
        elif db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username")):
            return apology("Username already taken", 403)
        elif db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email")):
            return apology("Email already taken", 403)

        db.execute("INSERT INTO users(fname, lname, username, dob, email, password) VALUES (:fname, :lname, :username, :dob, :email, :hash)",
            fname=request.form.get("fname"), lname=request.form.get("lname"),
            username=request.form.get("username"), dob=request.form.get("birth"),
            email=request.form.get("email"), hash=generate_password_hash(request.form.get("pwd")))

        rows = db.execute("SELECT * FROM users WHERE username = :username",
            username=request.form.get("username"))

        session["user_id"] = rows[0]["id"]
        return redirect("/home")
    else:
        return render_template("register.html")

    
# Update User Bio
@app.route("/writebio", methods=["GET", "POST"])
@login_required
def writebio():
    if request.method == "GET":
        id = session["user_id"]
        rows = db.execute("SELECT * FROM users WHERE id = :id", id=id)
        fname = rows[0]["fname"]
        lname = rows[0]["lname"]
        bio = rows[0]["bio"]
        return render_template("bio.html", fname=fname, lname=lname, bio=bio)
    else:
        bio = request.form.get("bio")
        id = session["user_id"]
        db.execute("UPDATE users SET bio = :bio WHERE id = :id", bio=bio, id=id)
        return redirect("/profile")
        
        

# User profile
@app.route("/profile")
@login_required
def profile():
    id = session["user_id"]
    rows = db.execute("SELECT * FROM users WHERE id = :id;", id=id)
    user_id = rows[0]["id"]
    fname = rows[0]["fname"]
    lname = rows[0]["lname"]
    email = rows[0]["email"]
    points = rows[0]["points"]
    problems = rows[0]["problems"]
    bio = rows[0]["bio"]
    return render_template("profile.html", id=id, fname=fname,
        lname=lname, email=email, problems=problems, points=points, bio=bio)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Change Password (You need to be logged in [obviously])
@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    id = session["user_id"]
    rows = db.execute("SELECT * FROM users WHERE id = :id", id=id)
    if request.method == "POST":
        password = request.form.get('oldpassword')
        if not check_password_hash(rows[0]["password"], password):
            return loggedapology("Invalid password", 403)

        newpassword = request.form.get('newpassword')
        confirmpassword = request.form.get('confirmpassword')

        if newpassword != confirmpassword:
            return loggedapology("Passwords do not match", 403)

        db.execute("UPDATE users SET password = :hash WHERE id = :id",
            hash=generate_password_hash(newpassword), id=session["user_id"])

        return redirect("/home")
    else:
        fname = rows[0]["fname"]
        lname = rows[0]["lname"]
        return render_template("changepassword.html", fname=fname, lname=lname)
    
@app.route('/viewprofile/<int:userid>')
@login_required
def viewprofile(userid):
    id=session["user_id"]
    rows = db.execute("SELECT * FROM users WHERE id = :id", id=id)
    fname = rows[0]["fname"]
    lname = rows[0]["lname"]
    otherUser = db.execute("SELECT * FROM users WHERE id = :id", id=userid)
    otherUserFname = otherUser[0]["fname"]
    otherUserLname = otherUser[0]["lname"]
    otherUserUsername = otherUser[0]["username"]
    otherUserProblems = otherUser[0]["problems"]
    otherUserPoints = otherUser[0]["points"]
    otherUserBio = otherUser[0]["bio"]
    return render_template("viewprofile.html", fname=fname, lname=lname, otherUserFname=otherUserFname, otherUserLname=otherUserLname, otherUserProblems = otherUserProblems, otherUserPoints=otherUserPoints, otherUserBio=otherUserBio, otherUserUsername=otherUserUsername)

# Error Handler

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)
    
# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
    
if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)