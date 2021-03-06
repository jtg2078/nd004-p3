#Full Stack Web Developer Nanodegree project 3


## How to run

setup vagrant

```
https://docs.google.com/document/d/1jFjlq_f-hJoAZP8dYuo5H3xY62kGyziQmiv9EPIA7tM/pub?embedded=true
```

getting source code

```
git clone git@github.com:jtg2078/nd004-p3.git

```

run

```
(copy contents of git cloned nd004-p3 folder into vagrant's catalog folder)

cd fullstack/vagrant
vagrant up
vagrant ssh
cd /vagrant/catalog
python application.py 
```

auth options

```
1. use default account to login
    * username: admin
    * password: admin
2. use google OAuth to login
```

database

```
- the repository already includes a sqlite db with data
- to setup a new empty database
    1. delete catalog.db
    2. (run) python database_setup.py 
```


## reference
* [nl2br filter](http://flask.pocoo.org/snippets/28/)
* [jinja2 api documentation](http://jinja.pocoo.org/docs/dev/api/)
* [Proper way to use **kwargs in Python](http://stackoverflow.com/questions/1098549/proper-way-to-use-kwargs-in-python)
* [What's the difference between “&nbsp;” and “ ”?](http://stackoverflow.com/questions/1357078/whats-the-difference-between-nbsp-and)
* [Testing Flask Applications](http://flask.pocoo.org/docs/0.10/testing/)
* [Google Design](https://www.google.com/design/)
* [SQLAlchemy Object Relational Tutorial](http://docs.sqlalchemy.org/en/rel_1_0/orm/tutorial.html)
* [How to change options of select with jQuery?](http://stackoverflow.com/questions/1801499/how-to-change-options-of-select-with-jquery)
* [pass post data with window.location.href](http://stackoverflow.com/questions/2367979/pass-post-data-with-window-location-href)
* [Make div 100% height of browser window](http://stackoverflow.com/questions/1575141/make-div-100-height-of-browser-window)
* [Twitter Bootstrap](http://getbootstrap.com/)
* [Full Stack Web Development with Flask](https://github.com/realpython/discover-flask/tree/part7)
* [WHO Model List of Essential Medicines](https://en.wikipedia.org/wiki/WHO_Model_List_of_Essential_Medicines#Anaesthetics)
* [The Flask Mega-Tutorial](http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vii-unit-testing)
* [Uploading Files](http://flask.pocoo.org/docs/0.10/patterns/fileuploads/)
* [How to get if checkbox is checked on flask](http://stackoverflow.com/questions/20941539/how-to-get-if-checkbox-is-checked-on-flask)
* [Generating Feeds with Flask](http://flask.pocoo.org/snippets/10/)
* [Handling URLs containing slash '/' character](http://flask.pocoo.org/snippets/76/)
* [Convert integer to string Jinja](http://stackoverflow.com/questions/19161093/convert-integer-to-string-jinja)
