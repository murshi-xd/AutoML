# oauth_client.py
from authlib.integrations.flask_client import OAuth
import os

def init_oauth(app):
    oauth = OAuth(app)
    oauth.register(
        name='google',
        client_id=os.environ.get("GOOGLE_CLIENT_ID"),
        client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
        access_token_url='https://oauth2.googleapis.com/token',
        authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v2/',
        userinfo_endpoint='https://www.googleapis.com/oauth2/v2/userinfo',
        client_kwargs={
            'scope': 'email profile',
            'token_endpoint_auth_method': 'client_secret_post'  # 👈 prevents OpenID parsing
        }
    )
    return oauth
