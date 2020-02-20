import os
import requests

from flask import Flask, session, render_template, redirect, request, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helper import login_required, decimal_c


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        try:
            username=request.form.get("username")
            password=request.form.get("password")
        except ValueError:
            return render_template("error.html", message="No username or Password")

        if not request.form.get("confirmation") == request.form.get("password"):
            return render_template("error.html", message="Password does not match confirmation")

        # if len(password) < 6:
        #     return render_template("error.html", message="Password less than 6 characters")
        #
        # if not any(char.isdigit() for char in password):
        #     return render_template("error.html", message="Password has not digits")


        hpass = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        # Query insertion
        if db.execute("SELECT username FROM users WHERE username = :username", {"username":username}).rowcount != 0:
            return render_template("error.html", message="Username Already exists")

        db.execute("INSERT INTO users(username, hash_password) VALUES(:username, :hash_password)",{"username":username, "hash_password":hpass})

        # Query database for username
        user = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username":username}).fetchone()
        db.commit()


        # Remember which user has logged in
        session["user_id"] = user["user_id"]

        # Redirect user to home page
        return redirect("/search")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        try:
            username=request.form.get("username")
            password=request.form.get("password")
        except ValueError:
            return render_template("error.html", message="No username or Password")

        # Query database for username
        user = db.execute("SELECT * FROM users WHERE username = :username",{"username":username}).fetchone()

        # Ensure username exists and password is correct
        if user is None or not check_password_hash(user["hash_password"], password):
            return render_template("error.html", message="Wrong Password")

        # Remember which user has logged in
        session["user_id"] = user["user_id"]

        # Redirect user to home page
        return redirect("/search")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("index.html")

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":

        # Ensure username was submitted
        try:
            search_type=request.form.get("search_type")
            search_value=request.form.get("search_value")
        except ValueError:
            return render_template("error.html", message="Please input searh type and value")

        # Query database for username
        books = db.execute(f"SELECT * FROM books WHERE {search_type} LIKE :search_value", {"search_type":search_type, "search_value":'%'+search_value+'%'}).fetchall()
        books2 = db.execute(f"SELECT * FROM books WHERE {search_type} LIKE :search_value", {"search_value":'%'+search_value.title()+'%'})

        if books is None or books2 is None:
            return render_template("error.html", message="No book with that name")
        # Redirect user to home page
        return render_template("books.html", books=books, books2=books2)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("search.html")

# load all information about a specific book(the reviews that have been written in the site and the ones from Goodreads as well)
@app.route("/books/<int:book_id>")
@login_required
def book(book_id):

    book = db.execute("SELECT * FROM books WHERE book_id = :book_id", {"book_id": book_id}).fetchone()
    reviews = db. execute("SELECT reviews.review, users.username FROM reviews JOIN users ON reviews.user_id=users.user_id WHERE reviews.book_id=:book_id",
        {"book_id":book_id}).fetchall()

    if book is None:
        return render_template("error.html", message="No such book.")

    res =  requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "13lRhRoBeLEZb2lATj08dw", "isbns": book["isbn"]})

    book_goodreads = res.json()

    return render_template("book.html", book=book, reviews=reviews, book_goodreads=book_goodreads["books"][0])

# leave a review and a rate about a specific book
@app.route("/review", methods=["POST"])
@login_required
def review():
    user_id = session["user_id"]

    try:
        rate = int(request.form.get("rate"))
        review = request.form.get("review")
        book_id = request.form.get("book_id")
    except ValueError:
        return render_template("error.html", message="Please leave a review and rate")

    review = db.execute("SELECT * FROM reviews WHERE book_id = :book_id AND user_id=:user_id", {"book_id": book_id, "user_id":user_id}).fetchone()

    if review:
        return render_template("error.html", message="You have already rated this book")
    db.execute("INSERT INTO reviews(review, book_id, user_id) VALUES (:review, :book_id, :user_id)",
            {"review":request.form.get("review"), "book_id":book_id, "user_id":session["user_id"]})

    book = db.execute("SELECT * FROM books WHERE book_id = :book_id", {"book_id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="No book with that id")
    review_count = int(book["review_count"]) + 1
    average_score = int(book["average_score"]) + rate/review_count
    db.execute("UPDATE books SET review_count = :review_count, average_score = :average_score WHERE book_id=:book_id",
            {"review_count":review_count, "average_score":average_score, "book_id":book_id})
    db.commit()
    return redirect(url_for('book', book_id=book.book_id))

# create JSON object with information from Database about a specific book
@app.route("/api/<isbn>")
def book_api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"error":"Invalid isbn"}), 422

    return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": book.review_count,
            "average_score": book.average_score
          })
