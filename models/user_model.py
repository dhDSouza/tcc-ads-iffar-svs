# Importando a extensão Bcrypt do Flask
from flask_bcrypt import Bcrypt

# Inicializando a instância do Bcrypt
bcrypt = Bcrypt()

# Definindo a classe User para representar um usuário
class User:
    def __init__(self, email, password):
        # Inicializando os atributos de email e senha
        self.email = email
        self.password = password

    def hash_password(self):
        # Método para gerar o hash da senha utilizando o Bcrypt
        self.password = bcrypt.generate_password_hash(self.password).decode('utf-8')

    def check_password(self, password):
        # Método para verificar se a senha fornecida corresponde ao hash armazenado
        return bcrypt.check_password_hash(self.password, password)
