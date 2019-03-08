#!/usr/bin/env python3
"""Backend of Item Catalog app."""

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    """Return index page."""
    return render_template('index.html')


@app.route('/login/')
def login():
    """Return page with login options."""
    return render_template('index.html')


@app.route('/categories/')
def showCategories():
    """Return categories page."""
    return render_template('index.html')


@app.route('/category/<int:categoryid>/')
def showCategoryItems(categoryid):
    """Return page with all items in a category."""
    return render_template('index.html')


@app.route('/category/<int:categoryid>/item/<int:itemid>/')
def showItems(categoryid, itemid):
    """Return page with description of specific item."""
    return render_template('index.html')


def main():
    """Serve up a webpage on localhost."""
    app.secret_key = 'key'
    app.run('localhost', port=8080, debug=True)


if __name__ == "__main__":
    main()
