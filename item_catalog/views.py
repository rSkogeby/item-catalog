#!/usr/bin/env python3
"""Backend of Item Catalog app."""

import random
import string
import httplib2
import requests
import json
import os

from flask import Flask, render_template, request, redirect, url_for, jsonify,\
    flash, g, make_response, SQLAlchemy
from flask import session as login_session
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from flask_login import LoginManager, login_required
from oauth2client.client import flow_from_clientsecrets, OAuth2WebServerFlow

from item_catalog.models import Base, Category, Item, User
import config

app = Flask(__name__)
app.secret_key = config.db_password()
app.config['SESSION_TYPE'] = 'filesystem'
app.debug = True
db = SQLAlchemy(app)
#engine = create_engine(config.db_url(),
#                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def getUserID(email):
    """Fetch user ID if in DB, else return None."""
    try:
        user = session.query(User).filter_by(username=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    """Fetch stored info on user."""
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    """Add new user to DB."""
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    newUser = User(username=login_session['username'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).\
        filter_by(username=login_session['username']).one()
    return user.id


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
    latest_items = session.query(Item).\
        order_by(desc(Item.creation_date)).limit(5).all()
    return render_template(
        'landingpage.html',
        categories=categories, categoryid=categoryid,
        itemid=itemid, latest_items=latest_items,
        login_session=login_session
    )


@app.route('/about-us/')
def aboutus():
    """Return an about us page describing what we are and who we do."""
    return render_template('aboutus.html', login_session=login_session)


@app.route('/privacy-policy/')
def privacy():
    """Return an about us page describing what we are and who we do."""
    return render_template('privacypolicy.html', login_session=login_session)


@app.route('/login/')
def login():
    """Return page with login options."""
    passthrough_value = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits
        ) for x in range(32)
    )
    login_session['state'] = passthrough_value
    return render_template('login.html', login_session=login_session)


@app.route('/login/google/')
def gconnect():
    """Login using Google."""
    if request.args.get('state') != login_session['state']:
        return 'Fail'
    flow = OAuth2WebServerFlow(
        client_id=config.google_client_id(),
        client_secret=config.google_client_secret(),
        scope='https://www.googleapis.com/auth/userinfo.email',
        redirect_uri=config.google_redirect_uri()
    )
    # Redirect the user to auth_uri on your platform.
    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)


@app.route('/logout/')
def logout():
    """Logout from session."""
    if 'access_token' in login_session:
        login_session.pop('access_token', None)
    del login_session['username']
    del login_session['picture']
    del login_session['credentials']
    del login_session['gplus_id']
    flash('You were signed out')
    return redirect(url_for('index'))


@app.route('/login/authorized')
def callback():
    """Callback function for Google login."""
    code = request.args.get('code')
    # Pass code provided by authorization server redirection to this function
    flow = OAuth2WebServerFlow(
        client_id=config.google_client_id(),
        client_secret=config.google_client_secret(),
        scope='https://www.googleapis.com/auth/userinfo.email',
        redirect_uri=config.google_redirect_uri()
    )
    credentials = flow.step2_exchange(code)
    # Supply access token to information request using httplib2
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.
           format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # Check user is not already logged in using gconnect
    gplus_id = credentials.id_token['sub']
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps("Current user is already connected."), 200
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in session for later use
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['provider'] = 'google'
    login_session['username'] = data['email']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # See if user exists in db if it doesn't, create a new one.
    user_id = getUserID(login_session['username'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    # Flash message on next page with a header
    flash_string = 'You are signed in as {}.'.format(login_session['username'])
    flash(flash_string)
    return redirect(url_for('index'))


@app.route('/category/<int:categoryid>/')
def showCategory(categoryid):
    """Return page with all items in a category."""
    categories = session.query(Category).all()
    itemid = None
    items = session.query(Item).filter_by(category_id=categoryid).all()
    return render_template(
        'categorydisplay.html',
        categories=categories, categoryid=categoryid,
        items=items, itemid=itemid,
        login_session=login_session
    )


@app.route('/warning/')
def warning():
    """Return warning page if the user does not have the correct privileges."""
    return render_template('warning.html')


@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    """Return page to add a NEW CATEGORY."""
    categories = session.query(Category).all()
    itemid = None
    categoryid = None
    if 'username' in login_session:
        if request.method == 'POST':
            new_category = Category(
                name=request.form['name'],
                user_id=login_session['user_id']
            )
            session.add(new_category)
            session.commit()
            return redirect(url_for('index'))
        elif request.method == 'GET':
            return render_template(
                'categorynew.html',
                categories=categories, categoryid=categoryid,
                itemid=itemid,
                login_session=login_session)
    else:
        return redirect(url_for('warning'))


@app.route('/category/<int:categoryid>/edit/', methods=['GET', 'POST'])
def editCategory(categoryid):
    """Return page to EDIT a CATEGORY."""
    categories = session.query(Category).all()
    itemid = None
    category = session.query(Category).filter_by(id=categoryid).one()
    creator = getUserInfo(category.user_id)
    if creator is None:
        return redirect(url_for('warning'))
    if 'username' in login_session\
            and creator.id == login_session.get('user_id'):
        if request.method == 'POST':
            if request.form.get('name') != '':
                category.name = request.form.get('name')
                session.add(category)
                session.commit()
            return redirect(url_for('showCategory', categoryid=categoryid))
        if request.method == 'GET':
            return render_template(
                'categoryedit.html', categories=categories,
                categoryid=categoryid, category=category,
                itemid=itemid, login_session=login_session
            )
    else:
        return redirect(url_for('warning'))


@app.route('/category/<int:categoryid>/delete/', methods=['GET', 'POST'])
def deleteCategory(categoryid):
    """Return page to DELETE a CATEGORY."""
    categories = session.query(Category).all()
    itemid = None
    category = session.query(Category).filter_by(id=categoryid).one()
    creator = getUserInfo(category.user_id)
    if creator is None:
        return redirect(url_for('warning'))
    if 'username' in login_session\
            and creator.id == login_session.get('user_id'):
        if request.method == 'POST':
            items = session.query(Item).filter_by(category_id=categoryid).all()
            for item in items:
                session.delete(item)
            session.delete(category)
            session.commit()
            return redirect(url_for('index'))
        elif request.method == 'GET':
            return render_template(
                'categorydelete.html', categories=categories,
                categoryid=categoryid, category=category,
                itemid=itemid,
                login_session=login_session
            )
    else:
        return redirect(url_for('warning'))


@app.route('/category/<int:categoryid>/item/<int:itemid>/')
def showItem(categoryid, itemid):
    """Return page with description of specific item."""
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id=categoryid).all()
    item = session.query(Item).\
        filter_by(category_id=categoryid, id=itemid).one()
    return render_template(
        'itemdisplay.html', categories=categories,
        categoryid=categoryid,
        items=items, item=item, itemid=itemid,
        login_session=login_session
    )


@app.route('/category/<int:categoryid>/item/new/', methods=['GET', 'POST'])
def newItem(categoryid):
    """Return page to add a new item to the category."""
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id=categoryid).all()
    itemid = None
    if 'username' in login_session:
        if request.method == 'POST':
            new_item = Item(
                name=request.form['name'],
                description=request.form['description'],
                category_id=categoryid,
                user_id=login_session['user_id']
            )
            session.add(new_item)
            session.commit()
            return redirect(url_for('showCategory', categoryid=categoryid))
        elif request.method == 'GET':
            return render_template(
                'itemnew.html',
                categories=categories, categoryid=categoryid,
                itemid=itemid, items=items,
                login_session=login_session
            )
    else:
        return redirect(url_for('warning'))


@app.route('/category/<int:categoryid>/item/<int:itemid>/edit/',
           methods=['GET', 'POST'])
def editItem(categoryid, itemid):
    """Return page to EDIT specific ITEM."""
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id=categoryid).all()
    category = session.query(Category).filter_by(id=categoryid).one()
    item = session.query(Item).filter_by(id=itemid).one()
    creator = getUserInfo(item.user_id)
    if creator is None:
        return redirect(url_for('warning'))
    if 'username' in login_session\
            and creator.id == login_session.get('user_id'):
        if request.method == 'POST':
            if request.form.get('name') != '':
                item.name = request.form.get('name')
            if request.form.get('description') != '':
                item.description = request.form.get('description')
            if request.form.get('category') != '':
                item.category_id = request.form.get('category')
            session.add(item)
            session.commit()
            return redirect(url_for('showCategory', categoryid=categoryid))
        elif request.method == 'GET':
            return render_template(
                'itemedit.html', categories=categories,
                categoryid=categoryid, category=category,
                itemid=itemid, items=items, item=item,
                login_session=login_session
            )
    else:
        return redirect(url_for('warning'))


@app.route('/category/<int:categoryid>/item/<int:itemid>/delete/',
           methods=['GET', 'POST'])
def deleteItem(categoryid, itemid):
    """Return page to DELETE specific ITEM."""
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id=categoryid).all()
    category = session.query(Category).filter_by(id=categoryid).one()
    item = session.query(Item).filter_by(id=itemid).one()
    creator = getUserInfo(item.user_id)
    if creator is None:
        return redirect(url_for('warning'))
    if 'username' in login_session and\
            creator.id == login_session.get('user_id'):
        if request.method == 'POST':
            session.delete(item)
            session.commit()
            return redirect(url_for('showCategory', categoryid=categoryid))
        elif request.method == 'GET':
            return render_template(
                'itemdelete.html', categories=categories,
                categoryid=categoryid, category=category,
                itemid=itemid, items=items, item=item,
                login_session=login_session
            )
    else:
        return redirect(url_for('warning'))


@app.route('/category.json/')
def categoryAPIEndpoint():
    """Return page to display JSON formatted information of category."""
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/category/<int:categoryid>.json/')
def itemAPIEndpoint(categoryid):
    """Return page to display JSON formatted information of item."""
    items = session.query(Item).filter_by(category_id=categoryid).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog.json/')
def catalogAPIEndpoint():
    """Return page to display JSON formatted information of whole catalog."""
    categories = session.query(Category).all()
    catalog = {}
    for category in categories:
        cats = category.serialize
        items = session.query(Item).filter_by(category_id=category.id).all()
        if items is not None:
            iser = [i.serialize for i in items]
            cats['Item'] = iser
        catalog[category.id] = cats
    return jsonify(Categories=catalog)


@app.route('/category/<int:categoryid>/item.json/')
def arbitraryItemAPIEndpoint(categoryid):
    """Return page to display JSON formatted information of arbitrary item."""
    items = session.query(Item).filter_by(category_id=categoryid).all()
    if len(items) == 0:
        response = make_response(
            json.dumps("This category has no items for display."), 204
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    item_number = random.randint(0, len(items)-1)
    return jsonify(Items=items[item_number].serialize)


def run():
    """Serve up a webpage on localhost."""

    app.secret_key = config.db_password()
    app.run(config.ip_address(), port=config.port(), debug=True)


if __name__ == "__main__":
    run()
