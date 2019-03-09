#!/usr/bin/env python3
"""Backend of Item Catalog app."""

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import session as login_session
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from flask_oauthlib.client import OAuth

from item_catalog.models import Base, Category, Item
from instance.config import getGoogleClientId, getGoogleSecret


app = Flask(__name__)
app.config['GOOGLE_ID'] = getGoogleClientId()
app.config['GOOGLE_SECRET'] = getGoogleSecret()
oauth = OAuth(app)

# Login methods
google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)



engine = create_engine('sqlite:///itemcatalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def index():
    """Return index page.
    
    The index page presents:
    - a header with the title of the website and a button that takes 
    you to the login page. If you are logged in it logs you out.
    - a categories menu that displays all available categories.
    - a column with the latest items added.
    """
    categories = session.query(Category).all()
    categoryid = None
    itemid = None
    latest_items = session.query(Item).order_by(desc(Item.creation_date)).limit(5).all()
    return render_template('landingpage.html', categories=categories, categoryid=categoryid, itemid=itemid, latest_items=latest_items, login_session=login_session)


@app.route('/login/')
def login():
    """Return page with login options."""
    return render_template('login.html')

@app.route('/login/google/')
def gconnect():
    """Login using Google."""
    return google.authorize(callback=url_for('gauthorized', _external=True))


@app.route('/logout/')
def glogout():
    """Logout from session."""
    login_session.pop('google_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def gauthorized():
    """Callback function for Google login."""
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    login_session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    #return jsonify({"data": me.data})
    return redirect(url_for('index'))


@google.tokengetter
def get_google_oauth_token():
    return login_session.get('google_token')


@app.route('/categories/')
def showCategories():
    """Return categories page."""
    return render_template('index.html')


@app.route('/category/<int:categoryid>/')
def showCategory(categoryid):
    """Return page with all items in a category."""
    categories = session.query(Category).all()
    itemid = None
    items = session.query(Item).filter_by(category_id=categoryid).all()
    return render_template('categorydisplay.html', categories=categories, categoryid=categoryid, items=items, itemid=itemid)


@app.route('/category/new/', methods=['GET','POST'])
def newCategory():
    """Return page to add a NEW CATEGORY."""
    categories = session.query(Category).all()
    itemid = None
    categoryid = None
    if request.method == 'POST':
        new_category = Category(name=request.form['name'])
        session.add(new_category)
        session.commit()
        return redirect(url_for('index'))
    elif request.method == 'GET':
        return render_template('categorynew.html', categories=categories, categoryid=categoryid, itemid=itemid)


@app.route('/category/<int:categoryid>/edit/', methods=['GET', 'POST'])
def editCategory(categoryid):
    """Return page to EDIT a CATEGORY."""
    categories = session.query(Category).all()
    itemid = None
    category = session.query(Category).filter_by(id=categoryid).one()
    if request.method == 'POST':
        if request.form.get('name') != '':
            category.name = request.form.get('name')
            session.add(category)
            session.commit()
        return redirect(url_for('showCategory', categoryid=categoryid))
    if request.method == 'GET':
        return render_template('categoryedit.html', categories=categories, categoryid=categoryid, category=category, itemid=itemid)


@app.route('/category/<int:categoryid>/delete/', methods=['GET', 'POST'])
def deleteCategory(categoryid):
    """Return page to DELETE a CATEGORY."""
    categories = session.query(Category).all()
    itemid = None
    category = session.query(Category).filter_by(id=categoryid).one()
    if request.method == 'POST':
        session.delete(category)
        session.commit()
        return redirect(url_for('index'))
    elif request.method == 'GET':
        return render_template('categorydelete.html', categories=categories, categoryid=categoryid, category=category, itemid=itemid)


@app.route('/category/<int:categoryid>/item/<int:itemid>/')
def showItem(categoryid, itemid):
    """Return page with description of specific item."""
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id=categoryid).all()
    item = session.query(Item).filter_by(category_id=categoryid, id=itemid).one()
    return render_template('itemdisplay.html', categories=categories,
        categoryid=categoryid, items=items, item=item, itemid=itemid)


@app.route('/category/<int:categoryid>/item/new/', methods=['GET','POST'])
def newItem(categoryid):
    """Return page to add a new item to the category."""
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id=categoryid).all()
    itemid = None
    if request.method == 'POST':
        new_item = Item(name=request.form['name'], 
            description=request.form['description'],
            category_id=categoryid,
            )
        session.add(new_item)
        session.commit()
        return redirect(url_for('showCategory', categoryid=categoryid))
    elif request.method == 'GET':
        return render_template('itemnew.html', categories=categories, categoryid=categoryid, itemid=itemid, items=items)


@app.route('/category/<int:categoryid>/item/<int:itemid>/edit/', methods=['GET', 'POST'])
def editItem(categoryid, itemid):
    """Return page to EDIT specific ITEM."""
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id=categoryid).all()
    category = session.query(Category).filter_by(id=categoryid).one()
    item = session.query(Item).filter_by(id=itemid).one()
    if request.method == 'POST':
        if request.form.get('name') != '':
            item.name = request.form.get('name')
        if request.form.get('description') != '':
            item.description = request.form.get('description')
        session.add(item)
        session.commit()
        return redirect(url_for('showCategory', categoryid=categoryid))
    elif request.method == 'GET':
        return render_template('itemedit.html', categories=categories, categoryid=categoryid, category=category, itemid=itemid, items=items, item=item)


@app.route('/category/<int:categoryid>/item/<int:itemid>/delete/', methods=['GET', 'POST'])
def deleteItem(categoryid, itemid):
    """Return page to DELETE specific ITEM."""     
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id=categoryid).all()
    category = session.query(Category).filter_by(id=categoryid).one()
    item = session.query(Item).filter_by(id=itemid).one()
    if request.method == 'POST':
        return redirect(url_for('showCategory', categoryid=categoryid))
    elif request.method == 'GET':
        return render_template('itemdelete.html', categories=categories, categoryid=categoryid, category=category, itemid=itemid, items=items, item=item)


@app.route('/category/JSON/')
def categoryAPIEndpoint():
    """Return page to display JSON formatted information of category."""
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/category/<int:categoryid>/JSON/')
def itemAPIEndpoint(categoryid):
    """Return page to display JSON formatted information of item."""
    items = session.query(Item).filter_by(category_id=categoryid).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog/JSON/')
def catalogAPIEndpoint():
    """Return page to display JSON formatted information of whole catalog."""    
    categories = session.query(Category).all()
    catalog = {}
    for category in categories:
        cats = category.serialize
        items = session.query(Item).filter_by(category_id=category.id).all()
        if items != None:
            iser = [i.serialize for i in items]
            cats['Item'] = iser
        catalog[category.id] = cats
    return jsonify(Categories=catalog)


def main():
    """Serve up a webpage on localhost."""
    app.secret_key = 'key'
    app.run('localhost', port=8080, debug=True)


if __name__ == "__main__":
    main()
