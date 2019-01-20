from flask_restplus import Namespace, Resource

api = Namespace('status', description='status')

@api.route('/')
class Status(Resource):
    def get(self):
        return 'OK'