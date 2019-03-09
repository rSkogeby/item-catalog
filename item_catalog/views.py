#!/usr/bin/env python3
"""Backend of Item Catalog app."""

from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from item_catalog import dummydatabase
from item_catalog.models import Base, Category, Item

app = Flask(__name__)

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
    return render_template('landingpage.html', categories=categories, categoryid=categoryid, itemid=itemid)


@app.route('/login/')
def login():
    """Return page with login options."""
    return render_template('landingpage.html')


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

    return render_template('itemdisplay.html', categories=categories,
        categoryid=categoryid, items=items, itemid=itemid)


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


@app.route('/category/<int:categoryid>/JSON/')
def categoryAPIEndpoint(categoryid):
    """Return page to display JSON formatted information of category."""
    return render_template('index.html')


@app.route('/category/<int:categoryid>/item/<int:itemid>/JSON/')
def itemAPIEndpoint(categoryid, itemid):
    """Return page to display JSON formatted information of item."""
    return render_template('index.html')


def main():
    """Serve up a webpage on localhost."""
    app.secret_key = 'key'
    app.run('localhost', port=8080, debug=True)


if __name__ == "__main__":
    main()
