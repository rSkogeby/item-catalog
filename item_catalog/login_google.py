#!/usr/bin/env python3
"""Sign-in using Google API."""

from flask import request, make_response
from flask import session as login_session
import json

def connect():
    """Connect to Google."""
    if request.args.get('state') != login_session.get('state'):
        user_prompt = 'Invalid state parameter.'
        response = make_response(json.dumps(user_prompt), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # 
    access_token = request.data
    if request.args.get('state') != login_session.get('state'):
        user_prompt = 'Invalid state parameter.'
        response = make_response(json.dumps(user_prompt), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    if request.args.get('state') != login_session.get('state'):
        user_prompt = 'Invalid state parameter.'
        response = make_response(json.dumps(user_prompt), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    if request.args.get('state') != login_session.get('state'):
        user_prompt = 'Invalid state parameter.'
        response = make_response(json.dumps(user_prompt), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    if request.args.get('state') != login_session.get('state'):
        user_prompt = 'Invalid state parameter.'
        response = make_response(json.dumps(user_prompt), 401)
        response.headers['Content-Type'] = 'application/json'
        return response