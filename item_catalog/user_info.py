#!/usr/bin/env python3
"""Get user info and create new user in database."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def getUserID(email):
    """Fetch user ID if in DB, else return None."""
    try:
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        user = session.query(User).filter_by(email=email).one()
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
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id
