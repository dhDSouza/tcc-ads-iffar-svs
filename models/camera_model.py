# Importando a classe ObjectId do módulo bson
from bson import ObjectId

# Definindo a classe Camera para manipulação de dados relacionados a câmeras
class Camera:
    def __init__(self, name=None, ip=None, linha=None, entrada=None):
        # Inicializando os atributos da câmera
        self.name = name
        self.ip = ip
        self.linha = linha
        self.entrada = entrada

    def add_camera(self, name, ip, linha=None, entrada=None):
        # Método para adicionar uma nova câmera ao banco de dados
        from app import mongo
        mongo.get_database().get_collection('cameras').insert_one({
            'name': name,
            'ip': ip,
            'linha': linha,
            'entrada': entrada
        })
    
    def list_cameras(self):
        # Método para listar todas as câmeras no banco de dados
        from app import mongo
        return list(mongo.get_database().get_collection('cameras').find())

    def list_cameras_contagem(self):
        # Método para listar câmeras com contagem definida de linha e entrada
        from app import mongo

        query = {'$and': [{'linha': {'$ne': None}}, {'entrada': {'$ne': None}}]}
        return list(mongo.get_database().get_collection('cameras').find(query))

    def get_camera_by_id(self, camera_id):
        # Método para obter uma câmera pelo seu ID no banco de dados
        from app import mongo
        return mongo.get_database().get_collection('cameras').find_one({'_id': ObjectId(camera_id)})

    def get_camera_by_ip(self, ip):
        # Método para obter uma câmera pelo seu endereço IP no banco de dados
        from app import mongo
        return mongo.get_database().get_collection('cameras').find_one({'ip': ip})

    def update_camera(self, camera_id, new_name, new_ip, new_linha=None, new_entrada=None):
        # Método para atualizar as informações de uma câmera no banco de dados
        from app import mongo
        mongo.get_database().get_collection('cameras').find_one_and_update(
            {'_id': ObjectId(camera_id)},
            {'$set': {'name': new_name, 'ip': new_ip, 'linha': new_linha, 'entrada': new_entrada}}
        )

    def delete_camera(self, camera_id):
        # Método para excluir uma câmera do banco de dados pelo seu ID
        from app import mongo
        mongo.get_database().get_collection('cameras').find_one_and_delete({'_id': ObjectId(camera_id)})
