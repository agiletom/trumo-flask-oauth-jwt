import os
import secrets
import requests
from urllib.parse import urlencode

from dotenv import load_dotenv
from flask import Flask, redirect, url_for, render_template, flash, session, current_app, request, abort, jsonify
from pymongo import MongoClient
from datetime import datetime
from os import environ as env
from flask_jwt_extended import JWTManager, create_access_token

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['OAUTH2_PROVIDERS'] = {
    'google': {
        'client_id': env.get('GOOGLE_CLIENT_ID'),
        'client_secret': env.get('GOOGLE_CLIENT_SECRET'),
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'token_url': 'https://accounts.google.com/o/oauth2/token',
        'userinfo': {
            'url': 'https://www.googleapis.com/oauth2/v3/userinfo',
            'email': lambda json: json['email'],
        },
        'scopes': ['https://www.googleapis.com/auth/userinfo.email'],
    },

    'github': {
        'client_id': env.get('GITHUB_CLIENT_ID'),
        'client_secret': env.get('GITHUB_CLIENT_SECRET'),
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'token_url': 'https://github.com/login/oauth/access_token',
        'userinfo': {
            'url': 'https://api.github.com/user/emails',
            'email': lambda json: json[0]['email'],
        },
        'scopes': ['user:email'],
    },
}

DATABASE_PORT = int(env.get("DATABASE_PORT", 27017))
client = MongoClient(env.get("DATABASE_HOST", "localhost"), DATABASE_PORT)
db = client[env.get("DATABASE_NAME", "flask-oauth-jwt")]

jwt = JWTManager(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/authorize/<provider>')
def oauth2_authorize(provider):
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    session['oauth2_state'] = secrets.token_urlsafe(16)

    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('oauth2_callback', provider=provider, _external=True),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })

    return redirect(provider_data['authorize_url'] + '?' + qs)

@app.route('/callback/<provider>')
def oauth2_callback(provider):
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}')
        return redirect(url_for('index'))

    if request.args['state'] != session.get('oauth2_state'):
        abort(401)

    if 'code' not in request.args:
        abort(401)

    response = requests.post(provider_data['token_url'], data={
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('oauth2_callback', provider=provider, _external=True),
    }, headers={'Accept': 'application/json'})

    if response.status_code != 200:
        abort(401)
    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        abort(401)

    response = requests.get(provider_data['userinfo']['url'], headers={
        'Authorization': 'Bearer ' + oauth2_token,
        'Accept': 'application/json',
    })
    if response.status_code != 200:
        abort(401)
    email = provider_data['userinfo']['email'](response.json())

    activity_type = "login"
    user = db.users.find_one()

    if not user: 
        user = db.users.insert_one({"email": email})
        activity_type = "signup"

    log_activity(user, activity_type)

    jwt_token = create_access_token(identity=str(user['_id']))

    flash(f'Logged in as {email}.')
    flash(f'Access token: {jwt_token}')

    return redirect(url_for('index'))

def log_activity(user, activity):
    db.activity_logs.insert_one({
        "user_id": user["_id"],
        "type": activity,
        "timestamp": datetime.utcnow()
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
