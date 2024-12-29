import json
import os

from db.db import MongoDbClient
from dotenv import load_dotenv
from flasgger import Swagger, swag_from
from flask import Flask, Response, request
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from utils.response import make_success_response

load_dotenv()
app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'API',
    'uiversion': 3
}
app.secret_key = os.getenv('FLASK_SECRET_KEY')

login_manager = LoginManager()
login_manager.init_app(app)

swagger = Swagger(app)

client = MongoDbClient(init_db=True)

class LoginUser(UserMixin):
    def __init__(self, **kwargs):
        self.id = kwargs.get("_id")
        self.username = kwargs.get("username")
        self.password_hash = kwargs.get("password")

@login_manager.user_loader
def load_user(user_id: str) -> LoginUser:
    user = client.get_user_by_id(user_id)
    return LoginUser(**user) if user else None

@app.route("/")
def home():
    return {}

@app.route("/register", methods=["POST"])
@swag_from("./swagger/register_user.yaml")
def register():
    return client.register_user(request.get_json())

@app.route("/login", methods=["POST"])
@swag_from("./swagger/login.yaml")
def login():
    if current_user and current_user.is_authenticated:
        return make_success_response("Already logged in")
    
    res: Response = client.login(request.get_json())
    if 200 <= res.status_code <= 299:
        payload = json.loads(res.get_data().decode('utf-8'))
        login_user(LoginUser(**payload))
        role = f" (role: {payload.get('role', '')})" if payload.get('role') else ""
        return make_success_response(f"Logged in successfully{role}")
    return res

@app.route("/logout", methods=["GET"])
@login_required
@swag_from("./swagger/logout.yaml")
def logout():
    if not current_user:
        return make_success_response("Already logged out")
    logout_user()
    return make_success_response("Logged out successfully")

@app.route("/promote", methods=["POST"])
@swag_from("./swagger/promote_user.yaml")
def promote_user():
    return client.promote_user(request.get_json())

@app.route("/demote", methods=["POST"])
@swag_from("./swagger/demote_user.yaml")
def demote_user():
    return client.demote_user(request.get_json())

@app.route("/cases", methods=["GET"])
@login_required
@swag_from("./swagger/get_cases.yaml")
def get_cases():
    return client.get_cases()

@app.route("/case", methods=["POST"])
@login_required
@swag_from("./swagger/upsert_case.yaml")
def upsert_case():
    return client.upsert_case(request.get_json())

if __name__ == '__main__':
    app.run(debug=False)