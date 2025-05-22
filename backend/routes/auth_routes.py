from flask import Blueprint, redirect, request, session, jsonify
from utils.oauth_client import init_oauth
from controllers.auth_controller import login_success_handler, store_user_in_db
import os


auth_bp = Blueprint('auth', __name__)
oauth = None

@auth_bp.record
def setup(state):
    global oauth
    oauth = init_oauth(state.app)

@auth_bp.route('/login/google')
def login_google():
    redirect_uri = request.url_root + 'auth/callback/google'
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/auth/callback/google')
def google_callback():
    token = oauth.google.authorize_access_token()
    userinfo = oauth.google.get("userinfo").json()  # ✅ correct fix

    session["user"] = {
        "provider": "google",
        "name": userinfo.get("name"),
        "email": userinfo.get("email"),
        "picture": userinfo.get("picture")
    }

    store_user_in_db(session["user"])  # ✅ ensure stored in MongoDB
    return redirect(os.environ.get("FRONTEND_URL", "http://localhost:5173"))

@auth_bp.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(os.environ.get("FRONTEND_URL", "/login"))

@auth_bp.route('/user')
def get_user():
    if 'user' in session:
        return jsonify(session['user'])
    return jsonify({"error": "Not logged in"}), 401
