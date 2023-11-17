from bson import ObjectId

class Camera:
    def __init__(self, name=None, ip=None):
        self.name = name
        self.ip = ip

    def add_camera(self, name, ip):
        from app import mongo
        mongo.get_database().get_collection('cameras').insert_one({'name': name, 'ip': ip})

    def list_cameras(self):
        from app import mongo
        return list(mongo.get_database().get_collection('cameras').find())

    def get_camera_by_id(self, camera_id):
        from app import mongo
        return mongo.get_database().get_collection('cameras').find_one({'_id': ObjectId(camera_id)})

    def get_camera_by_ip(self, ip):
        from app import mongo
        return mongo.get_database().get_collection('cameras').find_one({'ip': ip})

    def update_camera(self, camera_id, new_name, new_ip):
        from app import mongo
        mongo.get_database().get_collection('cameras').find_one_and_update(
            {'_id': ObjectId(camera_id)},
            {'$set': {'name': new_name, 'ip': new_ip}},
            return_document=True
        )

    def delete_camera(self, camera_id):
        from app import mongo
        mongo.get_database().get_collection('cameras').find_one_and_delete({'_id': ObjectId(camera_id)})