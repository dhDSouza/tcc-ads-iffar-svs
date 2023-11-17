from flask import Blueprint, render_template, url_for, request, jsonify, session, redirect
from models.user_model import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    from app import verificar_login
    if verificar_login():
        return render_template('index.html')
    
    return redirect(url_for('auth.login'))
 
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    from app import mongo
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        exist_user = mongo.get_database().get_collection('users').find_one({'email': email})
        
        if exist_user:
            user_email = exist_user.get('email')
            user_password = exist_user.get('password')
            user = User(user_email, user_password)

            user.hash_password()

            if user.check_password(password):
                session['user'] = user.email
                session.permanent = True
                return redirect(url_for('auth.index'))

            data = "Não autorizado!"
            return render_template('login.html', data=data)

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    from app import verificar_login
    if verificar_login():
        session.pop('user', None)
        return redirect(url_for('auth.index'))

    data = "Não autorizado!"
    return render_template('login.html', data=data)
