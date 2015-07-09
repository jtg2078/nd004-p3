from functools import wraps

# flask related imports
from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask import session as login_session

# database related imports
from sqlalchemy import create_engine, asc, desc
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

# category required decorator
def category_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        category_name = kwargs.get('category_name', '')
        category = (db_session.query(Category)
                    .filter(Category.name == category_name)
                    .first())
        if not category:
            flash('category with name {0} does not exist'.format(category_name))
            return redirect(url_for('home'))
        else:
            kwargs['category'] = category
            return f(*args, **kwargs)

    return wrap

# subcategory required decorator
def subcategory_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        category = kwargs.get('category', None)
        subcategory_name = kwargs.get('subcategory_name', '')
        subcategory = (db_session.query(Subcategory)
                                 .filter(Subcategory.name == subcategory_name)
                                 .filter(Subcategory.category_id == category.id)
                                 .first())
        if not subcategory:
            flash('subcategory with name {0} does not exist'.format(subcategory_name))
            return redirect(url_for('home'))
        else:
            kwargs['subcategory'] = subcategory
            return f(*args, **kwargs)

    return wrap

#  ------------------------------  index ------------------------------


@app.route("/")
def home():
    items = db_session.query(Item).order_by(desc(Item.added))
    catalog = db_session.query(Category).order_by(asc(Category.id))
    return render_template("index.html",
                           user=login_session.get('user'),
                           catalog=catalog,
                           latest_items=items)


#  ------------------------------  login / logout ------------------------------

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


#  ------------------------------  category ------------------------------


@app.route("/catalog/<category_name>/items")
@category_required
def show_category(category_name=None, category=None):
    catalog = db_session.query(Category).order_by(asc(Category.id))
    subcategories = (db_session.query(Subcategory)
                               .filter(Subcategory.category_id == category.id)
                               .order_by(asc(Subcategory.id)))
    items = (db_session.query(Item)
                       .filter(Item.category_id == category.id)
                       .order_by(asc(Item.id)))
    return render_template('category.html',
                           user=login_session.get('user'),
                           catalog=catalog,
                           category=category,
                           subcategories=subcategories,
                           items=items)


@app.route('/catalog/category/new', methods=['POST', 'GET'])
@login_required
def new_category():
    error = None
    if request.method == 'POST':
        category_name = request.form.get('name', '').strip()
        if category_name:
            category = Category(name=category_name)
            db_session.add(category)
            db_session.commit()
            flash('New category %s Successfully Created' % category.name)
            return redirect(url_for('home'))
        else:
            error = 'category name is missing'
    return render_template('category_new.html', error=error, user=login_session.get('user'))


@app.route("/catalog/<category_name>/edit", methods=['POST', 'GET'])
@login_required
@category_required
def edit_category(category_name=None, category=None):
    error = None
    if request.method == 'POST':
        category_name = request.form.get('name', '').strip()
        if category_name:
            category.name = category_name
            db_session.add(category)
            db_session.commit()
            flash('Category updated!')
            return redirect(url_for('show_category', category_name=category_name))
        else:
            error = 'category name is missing'
    return render_template('category_edit.html', category=category, user=login_session.get('user'), error=error)


@app.route("/catalog/<category_name>/delete", methods=['POST'])
@login_required
@category_required
def delete_category(category_name=None, category=None):
    db_session.delete(category)
    db_session.commit()
    flash('Category {0} deleted!'.format(category_name))
    return redirect(url_for('home'))


#  ------------------------------  subcategory ------------------------------

@app.route('/catalog/<category_name>/subcategory/new', methods=['POST', 'GET'])
@login_required
@category_required
def new_subcategory(category_name, category):
    error = None
    if request.method == 'POST':
        subcategory_name = request.form.get('name', '').strip()
        if subcategory_name:
            subcategory = Subcategory(name=subcategory_name,
                                      category_id=category.id)
            db_session.add(subcategory)
            db_session.commit()
            flash('New subcategory %s created successfully' % subcategory.name)
            return redirect(url_for('show_category', category_name=category_name))
        else:
            error = 'subcategory name is missing'
    return render_template('subcategory_new.html', category=category, error=error, user=login_session.get('user'))


@app.route("/catalog/<category_name>/subcategory/<subcategory_name>/edit", methods=['POST', 'GET'])
@login_required
@category_required
@subcategory_required
def edit_subcategory(category_name=None, category=None, subcategory_name=None, subcategory=None):
    error = None
    if request.method == 'POST':
        subcategory_name = request.form.get('name', '').strip()
        if subcategory_name:
            subcategory.name = subcategory_name
            db_session.add(subcategory)
            db_session.commit()
            flash('Subcategory updated!')
            return redirect(url_for('show_category', category_name=category_name))
        else:
            error = 'Subcategory name is missing'
    return render_template('subcategory_edit.html',
                           category=category,
                           subcategory=subcategory, user=login_session.get('user'), error=error)


@app.route("/catalog/<category_name>/subcategory/<subcategory_name>/delete", methods=['POST'])
@login_required
@category_required
@subcategory_required
def delete_subcategory(category_name=None, category=None, subcategory_name=None, subcategory=None):
    db_session.delete(subcategory)
    db_session.commit()
    flash('Subcategory {0} deleted!'.format(subcategory_name))
    return redirect(url_for('show_category', category_name=category_name))


#  ------------------------------  item ------------------------------


@app.route("/catalog/<category_name>/<item_name>")
def show_item(category_name=None, item_name=None):
    return "this is item {0}'s page".format(item_name)


@app.route("/catalog/item/new")
def new_item():
    return "this is add new item page"


@app.route("/catalog/<item_name>/edit")
def edit_item(item_name=None):
    return "this is item {0}'s edit page".format(item_name)


@app.route("/catalog/<item_name>/delete")
def delete_item(item_name=None):
    return "this is item {0}'s delete page".format(item_name)


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=8000)
