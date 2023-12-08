# Importando as bibliotecas necessárias
from flask import Flask, redirect, url_for, session
from dotenv import load_dotenv
from pymongo import MongoClient
from controllers.auth_controller import auth_bp
from controllers.camera_controller import camera_bp
from datetime import timedelta
import os

# Carregando as variáveis de ambiente a partir do arquivo .env
load_dotenv()

# Inicializando a conexão com o MongoDB
mongo = MongoClient()

# Definindo o tempo de vida permanente da sessão para 30 minutos
PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

# Inicializando o aplicativo Flask e especificando a pasta de modelos (templates)
app = Flask(__name__, template_folder='views')

# Configurando a URI do MongoDB a partir da variável de ambiente
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo = MongoClient(app.config['MONGO_URI'])

# Configurando a chave secreta para a aplicação Flask
app.secret_key = os.getenv('SECRET_KEY')

# Configurando o tempo de vida permanente da sessão
app.config['PERMANENT_SESSION_LIFETIME'] = PERMANENT_SESSION_LIFETIME

# Registrando os blueprints para as rotas definidas nos controllers
app.register_blueprint(auth_bp)
app.register_blueprint(camera_bp)

# Função para verificar se o usuário está logado
def verificar_login():
    return 'user' in session

# Rota padrão que redireciona para a página de autenticação
@app.route('/')
def index():
    return redirect(url_for('auth.index'))

# Inicializando o aplicativo Flask quando o script é executado diretamente
if __name__ == '__main__':
    app.run(debug=True)
