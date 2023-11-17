from flask import Flask, redirect, url_for, session
from dotenv import load_dotenv
from pymongo import MongoClient
from controllers.auth_controller import auth_bp
from controllers.camera_controller import camera_bp
from datetime import timedelta
import os

load_dotenv()
mongo = MongoClient()

PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

app = Flask(__name__, template_folder='views')

app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo = MongoClient(app.config['MONGO_URI'])

app.secret_key = os.getenv('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = PERMANENT_SESSION_LIFETIME

app.register_blueprint(auth_bp)
app.register_blueprint(camera_bp)

def verificar_login():
    return 'user' in session

@app.route('/')
def index():
    return redirect(url_for('auth.index'))

if __name__ == '__main__':
    app.run(debug=True)
