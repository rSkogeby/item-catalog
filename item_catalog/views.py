#!/usr/bin/env python3
""" """

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


def main():
    """"""
    app.secret_key = 'key'
    app.run('localhost', port=8080, debug=True)


if __name__ == "__main__":
    main()
