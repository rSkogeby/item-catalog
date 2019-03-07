#!/usr/bin/env python3
""" """

from flask import Flask

app = Flask(__name__)


def main():
    """"""
    app.secret_key = 'key'
    app.run('localhost', debug=True)


if __name__ == "__main__":
    main()
