A Walk-Through
In this walk-through, you will build a subset of the "I Want A Pony" application that has been used extensively through the SQLAlchemy articles. If you haven't already set up your database, go to Setting up your database in Connecting SQLAlchemy To PostgreSQL and follow the instructions on setting up a database, a user/password, and creating the tables and relationships.

Install the dependencies
Create a new project directory named pony. In your Terminal, change the working directory to the pony directory you just created. In there, use pipenv to install Flask, Psycopg2, SQLAlchemy, and Flask-SQLAlchemy. Also, since you'll be working in a virtual environment, install pycodestyle as a development dependency.

For WSL Only
If you haven't already prepared your computer for running SQLAlchemy, please install postgresql-common using apt. This is required for the psycopg2-binary install.

sudo apt install postgresql-common
For both WSL and macOS
Install the dependencies for your application with your currently activated Python. (Make sure it's a 3.9 version. If it isn't, activate one with pyenv.)

pipenv install Flask psycopg2-binary SQLAlchemy \
               Flask-SQLAlchemy --python "$PYENV_ROOT/shims/python"
Now, install the development dependencies.

pipenv install --dev pycodestyle
Activate your virtual environment with pipenv shell.

Getting the application running
Open up the pony directory in Visual Studio Code. Create a directory named app in the project directory. Create and open a file named __init__.py in the app directory. After the Python environment initializes and tells you no linter is installed, click the "Select Linter" button, and choose "pycodestyle" from the dropdown.

In the __init__.py file, put this code in it which declares a configuration class, creates and configures the Flask application, and creates and configures the SQLAlchemy object from Flask-SQLAlchemy.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import environ


class Config:
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL") or \
        "postgresql://sqlalchemy_test:password@localhost/sqlalchemy_test"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


flask_app = Flask(__name__)
flask_app.config.from_object(Config)
db = SQLAlchemy(flask_app)
In the app directory, still, create a file named models.py. In there, add the following mapping class for Pony.

from app import db


class Pony(db.Model):
    __tablename__ = 'ponies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    birth_year = db.Column(db.Integer)
    breed = db.Column(db.String(255))
In the app directory, still, create a file named routes.py. In there, add the following code.

from app import flask_app as app
from app.models import Pony
from flask import render_template


@app.route("/")
@app.route("/index")
def index():
    pony_count = Pony.query.count()
    return render_template("index.html", pony_count=pony_count)
Create a templates directory in the app directory. In the templates directory, create an index.html file with the following content.

<html>
  <head>
    <title>I Want A Pony</title>
  </head>
  <body>
    <h1>There are currently {{ pony_count }} ponies!</h1>
  </body>
</html>
Finally, back in the project directory, create a file named pony.py. In that file, put the following two imports which initializes the Flask application and, then, loads the routes.

from app import flask_app as app
from app import routes
You should now have a runnable application. Run it with the following command which will put Flask in development mode and runs the pony.py as the main application.

FLASK_ENV=development FLASK_APP=pony.py flask run
Navigate to http://localhost:5000 and see how many ponies you have!

Create a link and pony list page
Back in the index.html file, replace the pony count with a link for the pony count:

<a href="{{ url_for('ponies') }}">
  {{ pony_count }} ponies!
</a>
In the routes.py file, create a method named "ponies" that queries the database for all of the ponies and passes them to a template.

@app.route("/ponies")
def ponies():
    ponies = Pony.query.all()
    return render_template("ponies.html", ponies=ponies)
Now, add a new file in the templates directory named ponies.html. In there, loop over the collection of ponies and make a table that contains their name, birth year, and breed. At the top of the page, put a link back to the home page.

You should now be able to see all the ponies and go back and forth between the pony list page and the home page.

Create a new pony
In the models.py, add the mapping for the Owners model.

class Owner(db.Model):
    __tablename__ = "owners"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255))

    ponies = db.relationship("Pony", back_populates="owner")
Add the foreign key and relationship to the Pony class that points back to its owner.

# Add these lines to the Pony class declaration
owner_id = db.Column(db.Integer, db.ForeignKey("owners.id"))

owner = db.relationship("Owner", back_populates="ponies")
In the ponies.html page, add a link that uses the url_for function to go to the "add_pony" function.

<a href="{{ url_for('add_pony')}}">Add a new pony</a>
Add an "add_pony" function that responds to the route "/ponies/new" route in the routes.py module. Query all of the Owners from the database. Render the template "pony_form.html" and pass the list of owners to it. At the top of routes.py, make sure you add Owner to the list of imports from app.models.

@app.route("/ponies/new")
def add_pony():
    owners = Owner.query.order_by(Owner.last_name, Owner.first_name).all()
    return render_template("pony_form.html", owners=owners)
In the templates directory, create a file named pony_form.html. Add the following HTML to the new file.

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Add Pony! - I Want A Pony</title>
</head>
<body>
  <header>
    <a href="{{ url_for('index') }}">Home</a>
    <a href="{{ url_for('ponies')}}">Back to pony list</a>
  </header>
  <fieldset>
    <legend>Add new pony</legend>
    <form method="post" action="/ponies/new">
      <div>
        <label for="name">Name</label>
        <input type="text" name="name" id="name" required>
      </div>
      <div>
        <label for="birth_year">Birth year</label>
        <input type="number" name="birth_year" id="birth_year" required>
      </div>
      <div>
        <label for="breed">Breed</label>
        <input type="text" name="breed" id="breed" required>
      </div>
      <div>
        <label for="owner_id">Owner id</label>
        <select name="owner_id" id="owner_id">
          {% for owner in owners %}
            <option value="{{ owner.id }}">
              {{ owner.last_name }}, {{ owner.first_name }}
            </option>
          {% endfor %}
        </select>
      </div>
      <div>
        <button type="submit">Create your new pony</button>
      </div>
    </form>
  </fieldset>
</body>
</html>
You should be able to see the form, now, when you click the "Add a new pony" link on the pony list page.

Back in the routes.py file, add redirect, request, and url_for to the imports from flask.

from flask import redirect, render_template, request, url_for
Also, import db from the app module.

from app import db, flask_app as app
To handle the form submission, change the route mapping on add_pony to handle both GETs and POSTs. In the add_pony function, if the method of the request is POST, then try to create a new pony and set it to the values submitted in the form. After committing the session, redirect to the list of ponies.

@app.route("/ponies/new", methods=["GET", "POST"])
def add_pony():
    if request.method == "POST":
        pony = Pony(**request.form)
        db.session.add(pony)
        db.session.commit()
        return redirect(url_for("ponies"))
    owners = Owner.query.order_by(Owner.last_name, Owner.first_name).all()
    return render_template("pony_form.html", owners=owners)
You can now add ponies to you application!

Deleting a pony
In the ponies.html file, add a new empty table header tag after the one that contains the "Breed" header. Then, in the body of the table, add a new table data tag that contains a form that posts to the URL for a function named "delete_pony" with the current pony's id. The form should have a button the reads "Delete" in it.

<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Birth year</th>
      <th>Breed</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    {% for pony in ponies %}
      <tr>
        <td>{{ pony.name }}</td>
        <td>{{ pony.birth_year }}</td>
        <td>{{ pony.breed }}</td>
        <td>
          <form method="POST" action="{{ url_for('delete_pony', id=pony.id) }}">
            <button type="submit">Delete</button>
          </form>
        </td>
      </tr>
    {% endfor %}
  </tbody>
</table>
Now, create a new route function named "delete_pony" in the routes.py file. It should have the route "/ponies/int:id/delete" and only handle POSTs. In it, query the specified Pony object, delete it, and commit that delete. Redirect back to the pony list page.

@app.route("/ponies/<int:id>/delete", methods=["POST"])
def delete_pony(id):
    pony = Pony.query.get(id)
    db.session.delete(pony)
    db.session.commit()
    return redirect(url_for("ponies"))
Now, you can also delete ponies! Great job!

That concludes the walk-through. This should give you enough understanding of how to use SQLAlchemy and Flask-SQLAlchemy with your Flask application so that you can build data-driven Web applications.