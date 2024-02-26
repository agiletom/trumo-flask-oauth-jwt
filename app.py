import secrets
from urllib.parse import urlencode

from dotenv import load_dotenv
from flask import Flask, redirect, url_for, render_template, session, current_app, abort
from pymongo import MongoClient
from os import environ as env

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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
