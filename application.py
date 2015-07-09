from functools import wraps
from datetime import datetime
import re
import collections

# flask related imports
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import session as login_session

# jinja2 related
from jinja2 import evalcontextfilter, Markup, escape
_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


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


#  ------------------------------  jinja2 ------------------------------


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
                          for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

#  ------------------------------  db helpers ------------------------------


def get_category(category_name):
    """return first category with given name"""
    return (db_session.query(Category).filter(Category.name == category_name).first())


def get_subcategory(category, subcategory_name):
    """return first subcategory with given name and in given category"""
    return (db_session.query(Subcategory)
                      .filter(Subcategory.name == subcategory_name)
                      .filter(Subcategory.category_id == category.id)
                      .first())


def get_item(category, item_name):
    """return first item with given name from given category"""
    return (db_session.query(Item)
                      .filter(Item.category_id == category.id)
                      .filter(Item.name == item_name)
                      .first())


def list_subcategory(category):
    """return list of subcategory under given category"""
    return (db_session.query(Subcategory)
                      .filter(Subcategory.category_id == category.id)
                      .order_by(asc(Subcategory.id)))

#  ------------------------------  decorators ------------------------------


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
        category = get_category(category_name)
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
        category = kwargs.get('category')
        subcategory_name = kwargs.get('subcategory_name', '')
        subcategory = get_subcategory(category, subcategory_name)
        if not subcategory:
            flash('subcategory with name {0} does not exist'.format(subcategory_name))
            return redirect(url_for('show_category', category_name=category.name))
        else:
            kwargs['subcategory'] = subcategory
            return f(*args, **kwargs)

    return wrap


# item required decorator
def item_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        category = kwargs.get('category')
        item_name = kwargs.get('item_name', '')
        item = get_item(category, item_name)
        if not item:
            flash('item with name {0} does not exist'.format(item_name))
            return redirect(url_for('show_category', category_name=category.name))
        else:
            kwargs['item'] = item
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
    all_items = (db_session.query(Item)
                           .filter(Item.category_id == category.id)
                           .order_by(asc(Item.id)))
    subcategories_items = collections.defaultdict(list)
    items = []
    for item in all_items:
        if item.subcategory_id:
            subcategories_items[item.subcategory_id].append(item)
        else:
            items.append(item)
    return render_template('category.html',
                           user=login_session.get('user'),
                           catalog=catalog,
                           category=category,
                           subcategories=subcategories,
                           subcategories_items=subcategories_items,
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


@app.route("/catalog/<category_name>/subcategories.json")
@category_required
def api_subcategories(category_name=None, category=None):
    subcategories = list_subcategory(category)
    return jsonify({"subcategories": [i.serialize for i in subcategories]})


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
@category_required
@item_required
def show_item(category_name=None, category=None, item_name=None, item=None):
    return render_template('item.html', user=login_session.get('user'), category=category, item=item)


@app.route("/catalog/item/new", methods=['POST', 'GET'])
@login_required
def new_item():
    error = None
    name = None
    description = None
    from_category = request.args.get('default_category', None)
    category_name = from_category
    subcategory_name = None
    catalog = db_session.query(Category).order_by(asc(Category.id))
    subcategories = []
    if request.method == 'POST':
        category = None
        subcategory = None
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category_name = request.form.get('category', '').strip()
        subcategory_name = request.form.get('subcategory', '').strip()
        if not name:
            error = 'item name is missing'
        elif not category_name:
            error = 'category is missing'
        else:
            category = get_category(category_name)
            if not category:
                error = 'category is not found'
            else:
                if subcategory_name:
                    subcategory = get_subcategory(category, subcategory_name)
                    if not subcategory:
                        error = 'subcategory is not found'
        if error is None:
            item = Item(name=name,
                        description=description,
                        added=datetime.now(),
                        updated=datetime.now(),
                        category_id=category.id)
            if subcategory:
                item.subcategory_id = subcategory.id
            db_session.add(item)
            db_session.commit()
            flash('New item %s successfully created' % name)
            return redirect(url_for('show_category', category_name=category_name))
    if category_name:
        category = get_category(category_name)
        if category:
            subcategories = list_subcategory(category)
    return render_template('item_new_edit.html',
                           error=error,
                           user=login_session.get('user'),
                           name=name,
                           description=description,
                           category_name=category_name,
                           subcategory_name=subcategory_name,
                           subcategories=subcategories,
                           from_category=from_category,
                           catalog=catalog,
                           edit_or_add="Add")


@app.route("/catalog/<category_name>/<item_name>/edit", methods=['POST', 'GET'])
@login_required
@category_required
@item_required
def edit_item(category_name=None, category=None, item_name=None, item=None):
    error = None
    name = item.name
    description = item.description
    category_name = item.category.name
    subcategory_name = item.subcategory.name if item.subcategory else None
    subcategories = list_subcategory(category)
    from_category = category_name
    catalog = db_session.query(Category).order_by(asc(Category.id))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category_name = request.form.get('category', '').strip()
        subcategory_name = request.form.get('subcategory', '').strip()
        if name:
            item.name = name
        if description:
            item.description = description
        if category_name:
            category = get_category(category_name)
            if not category:
                error = 'category is not found'
            else:
                item.category_id = category.id
                if subcategory_name:
                    subcategory = get_subcategory(category, subcategory_name)
                    if not subcategory:
                        error = 'subcategory is not found'
                    else:
                        item.subcategory_id = subcategory.id
                else:
                    item.subcategory_id = None
        if not error:
            db_session.add(item)
            db_session.commit()
            flash('item {0} updated!'.format(item_name))
            return redirect(url_for('show_category', category_name=category_name))
    return render_template('item_new_edit.html',
                           error=error,
                           user=login_session.get('user'),
                           name=name,
                           description=description,
                           category_name=category_name,
                           subcategory_name=subcategory_name,
                           subcategories=subcategories,
                           from_category=from_category,
                           catalog=catalog,
                           edit_or_add="Edit")


@app.route("/catalog/<category_name>/<item_name>/delete", methods=['POST'])
@login_required
@category_required
@item_required
def delete_item(category_name=None, category=None, item_name=None, item=None):
    db_session.delete(item)
    db_session.commit()
    flash('Item {0} deleted!'.format(item_name))
    return redirect(url_for('show_category', category_name=category_name))




if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=8000)
