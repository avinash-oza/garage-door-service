from flask import request
from flask_restplus import Resource, fields

from . import api
from .utils import get_garage_dict_status, control_garage

GarageStatusModel = api.model('GarageStatusModel', {
    'garage_name': fields.String(),
    'status': fields.String(),
    'error': fields.Boolean(),
    'is_open': fields.Boolean(default=True),
    'message': fields.String(allow_null=True)
})

GarageStatusResponseModel = api.model('GarageStatusResponseModel',
                                      {'status': fields.List(fields.Nested(GarageStatusModel)),
                                       'type': fields.String(default='STATUS'),
                                       'id': fields.String()
                                       }
                                      )


@api.route('/garage/status')
class GarageStatusResource(Resource):
    @api.marshal_with(GarageStatusResponseModel)
    def get(self, garage_name='ALL'):
        return {'status': get_garage_dict_status(garage_name), 'type': 'STATUS'}


@api.route('/garage/trigger/<string:garage_name>')
class GarageTriggerResource(Resource):
    def post(self, garage_name):
        response = {'type': 'STATUS'}
        raw_input_message = request.json  # the message as it was sent in

        message_type = raw_input_message['type']
        garage_name = garage_name.upper()
        action = raw_input_message['action']

        if message_type == 'CONTROL':
            response['status'] = [control_garage(garage_name, action)]
        else:
            response['status'] = [{'message': 'Invalid action passed', 'error': True}]

        return response
