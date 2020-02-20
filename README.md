# Project 1

Web Programming with Python and JavaScript

In this project, I was tasked to build a book review web app. Users are able to register for your website and then log in using their username and password. Once they log in, they are able to search for books, leave reviews for individual books, and see the reviews made by other people. I also had to use the a third-party API by Goodreads, another book review website, to pull in ratings from a broader audience. Finally, users are able to query for book details and book reviews programmatically via your website’s API.

The objectives of this project were:
1. Become more comfortable with Python.
2. Gain experience with Flask.
3. Learn to use SQL to interact with databases.


The files contained within are as following:
1. import: a file containing the import.py and the books.csv used to store within the database the books offered by CS50
2. static: a file containing my scss and my css file with my own styling for my web app
3. templates: this is where my templates for my web app are contained. A few details I may have to point out is:
            a. the book.html file contains information about each book, as well as the number of reviews and the and the average score, from both my web app and goodreads. Here the user can also rate the book and see all the reviews left by every other user.
            b. books.html is where the user will be led should he makes a search.
            c. error.html is a very simple template used to handle all the error that may occur during the user's experience(ex. the user sends an empty input)
            d. index.html is not used as of now
            e. search.html is the page where the user can search for book by the author, title, year or isbn
4. helper.py is where I stored the login_required function so as to prevent unregistered users from accessing the site. It also contains a function I did not actually use
5. requirements.txt I also included requests which I had not installed.

Getting Started

To run this web app a PostgreSQL database must be used. It's possible to set up PostgreSQL locally on your own computer.

1. Navigate to https://www.heroku.com/, and create an account if you don’t already have one.
2. On Heroku’s Dashboard, click “New” and choose “Create new app.”
3. Give your app a name, and click “Create app.”
4. On your app’s “Overview” page, click the “Configure Add-ons” button.
5. In the “Add-ons” section of the page, type in and select “Heroku Postgres.”
6. Choose a plan, which will give you access to a free PostgreSQL database that will support up to 10,000 rows of data. Click “Provision.”
7. Now, click the “Heroku Postgres :: Database” link.
8. You should now be on your database’s overview page. Click on “Settings”, and then “View Credentials.” This is the information you’ll need to log into your database. You can access the database via Adminer, filling in the server (the “Host” in the credentials list), your username (the “User”), your password, and the name of the database, all of which you can find on the Heroku credentials page.

To run the web app:

1. Run pip install -r requirements.txt
2. Set the environment varibel FLASK_APP to be application.py and set the DATABASE_URL to be the URI of your database.
3. Run flask run
