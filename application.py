from functools import wraps

# flask related imports
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session

# database related imports
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Subcategory, Item

# connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

app = Flask(__name__)
app.secret_key = '3\x8b<\xbbP\x01\xc29< \xbbw\xea\xbf~\x8a\xbb$\xb9\x9e\x0cx\x88\xc4'


# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' in login_session:
            return f(*args, **kwargs)
        else:
            flash('You need to log in first')
            return redirect(url_for('home'))

    return wrap


@app.route("/")
def home():
    return render_template("index.html", user=login_session.get('user'))


@app.route("/login", methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'invalid credential, please try again'
        else:
            login_session['user'] = 'admin'
            flash('You are now logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route("/logout")
@login_required
def logout():
    login_session.pop('user', None)
    flash('You are now logged out')
    return redirect(url_for('home'))


@app.route("/catalog/<category_name>/items")
def category(category_name=None):
    return "this is the {0}'s items listing page".format(category_name)


@app.route('/catalog/category/new', methods=['POST'])
@login_required
def new_category():
    new_category = Category(name=request.form['name'])
    db_session.add(new_category)
    db_session.commit()
    flash('New Category %s Successfully Created' % new_category.name)
    return redirect(url_for('home'))


@app.route("/catalog/<category_name>/<item_name>")
def item(category_name=None, item_name=None):
    return "this is item {0}'s page".format(item_name)


@app.route("/catalog/<item_name>/edit")
def edit_item(item_name=None):
    return "this is item {0}'s edit page".format(item_name)


@app.route("/catalog/<item_name>/delete")
def delete_item(item_name=None):
    return "this is item {0}'s delete page".format(item_name)


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=8000)
