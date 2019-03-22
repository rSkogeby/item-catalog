#!/usr/bin/env python3
"""Config file for validating .env variables and putting them into objects."""
import os


def ip_address():
    user_input = os.environ.get('LISTEN_INTERFACE', None)
    verified_input = user_input
    return verified_input


def port():
    user_input = os.environ.get('LISTEN_PORT', None)
    verified_input = user_input
    return verified_input


def db_password():
    user_input = os.environ.get('DATABASE_PASSWORD', None)
    verified_input = user_input
    return verified_input


def db_url():
    user_input = os.environ.get('DATABASE_URL', None)
    verified_input = user_input
    return verified_input


def google_client_id():
    user_input = os.environ.get('GOOGLE_CLIENT_ID', None)
    verified_input = user_input
    return verified_input


def google_client_secret():
    user_input = os.environ.get('GOOGLE_CLIENT_SECRET', None)
    verified_input = user_input
    return verified_input


def google_redirect_uri():
    user_input = os.environ.get('GOOGLE_REDIRECT_URI', None)
    verified_input = user_input
    return verified_input
