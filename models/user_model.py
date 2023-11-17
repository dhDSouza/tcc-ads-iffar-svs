from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def hash_password(self):
        self.password = bcrypt.generate_password_hash(self.password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
