#!/usr/bin/env python3
from item_catalog.views import app
import config


if __name__ == "__main__":
    app.secret_key = config.db_password()
    app.run()
