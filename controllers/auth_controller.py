# Importando as bibliotecas necessárias do Flask
from flask import Blueprint, render_template, url_for, request, jsonify, session, redirect

# Importando a classe User do modelo user_model
from models.user_model import User

# Criando o blueprint 'auth' para as rotas relacionadas à autenticação
auth_bp = Blueprint('auth', __name__)

# Rota principal que redireciona para a página de login ou para a lista de câmeras se o usuário estiver autenticado
@auth_bp.route('/')
def index():
    from app import verificar_login
    if verificar_login():
        return redirect(url_for('camera.listar_cameras'))
    
    return redirect(url_for('auth.login'))

# Rota para login, aceitando métodos GET e POST
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    from app import mongo

    # Verificando se a requisição é do tipo POST (submissão do formulário de login)
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Verificando se o usuário com o email fornecido existe no banco de dados
        exist_user = mongo.get_database().get_collection('users').find_one({'email': email})
        
        if exist_user:
            user_email = exist_user.get('email')
            user_password = exist_user.get('password')
            user = User(user_email, user_password)

            user.hash_password()

            # Verificando se a senha fornecida corresponde à senha no banco de dados
            if user.check_password(password):
                session['user'] = user.email
                session.permanent = True
                return redirect(url_for('auth.index'))

            data = "Não autorizado!"
            return render_template('login.html', data=data)

    # Se a requisição não for POST, renderiza a página de login
    return render_template('login.html')

# Rota para fazer logout
@auth_bp.route('/logout')
def logout():
    from app import verificar_login
    if verificar_login():
        # Removendo o usuário da sessão para fazer logout
        session.pop('user', None)
        return redirect(url_for('auth.index'))

    data = "Não autorizado!"
    return render_template('login.html', data=data)
