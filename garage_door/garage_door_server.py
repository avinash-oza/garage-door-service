import datetime
import json

import boto3
import requests
from flask import request
from flask_restplus import Resource, fields, marshal

from . import app, api
from .pi_funcs import trigger_garage, get_garage_status, SORTED_KEYS


def control_garage(garage_name, action):
    response = {'garage_name': garage_name, 'error': True}

    # Check what the current location is
    garage_status = get_garage_status(garage_name)

    current_garage_status = str(garage_status)

    response['status'] = current_garage_status
    if garage_status.is_open and action == 'OPEN':
        response['message'] = 'Trying to open garage that is already open'
    elif not garage_status.is_open and action == 'CLOSE':
        response['message'] = 'Trying to close garage that is already closed'
    else:
        try:
            trigger_garage(garage_name)
        except:
            response['message'] = 'AN ERROR OCCURED WHILE TRIGGERING THE RELAY'
        else:
            response['error'] = False
            response['message'] = 'TRIGGERED {0} GARAGE TO {1}. OLD POSITION: {2}'.format(garage_name, action, current_garage_status)

    return response


def get_garage_dict_status(garage_name):
    response = []
    if garage_name.lower() == 'all':
        garage_name = SORTED_KEYS
    else:
        garage_name = [garage_name]

    for one_garage in garage_name:
        one_response = {'error': False}
        try:
            garage_status = get_garage_status(one_garage)
        except Exception as e:
            one_response['error'] = True
            one_response['status'] = str(e)
        else:
            one_response['status'] = str(garage_status)
            one_response['is_open'] = garage_status.is_open

            one_response['garage_name'] = garage_status.name
            one_response['status_time'] = datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')

        response.append(one_response)

    return response

# web related logic

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


#TODO: Maybe a better way to keep track of this
class MessageType(fields.Raw):
    def format(self, value):
        return value.upper() if value.upper() in ('STATUS', 'CONTROL') else None

class ActionType(fields.Raw):
    def format(self, value):
        return value.upper() if value.upper() in ('OPEN', 'CLOSE') else None

class GarageNameType(fields.Raw):
    def format(self, value):
        return value.upper() if value.upper() in ('LEFT', 'RIGHT', 'ALL') else None


SNSMessageModel = api.model('SNSMessageModel', {
    'type': MessageType,
    'action': ActionType,
    'garage_name': GarageNameType
})


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


@api.route('/sns-callback')
class SNSCallbackResource(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        #TODO: queue name from config
        sqs = boto3.resource('sqs')
        self._queue = sqs.get_queue_by_name(QueueName='garage-responses')

    def post(self):
        try:
            data = json.loads(request.data.decode('utf-8'))
        except Exception as e:
            app.logger.exception("exception parsing {}".format(request.data))
        else:
            if data['Type'] == 'SubscriptionConfirmation' and 'SubscribeURL' in data:
                # call the subscription url to confirm
                app.logger.info("Subscribe URL is {}".format(data['SubscribeURL']))
                requests.get(data['SubscribeURL'])
            elif data['Type'] == 'Notification':
                # extract out the message and process
                app.logger.info("Message is {}".format(data))
                self.process_sns_message(data)
            else:
                app.logger.error("Couldnt process message: {}".format(data))

        return 'OK\n'

    def process_sns_message(self, data):
        # message that came via SNS
        message_id = data['MessageId']
        raw_input_message = json.loads(data['Message']) # the message as it was sent in
        cleaned_message = marshal(raw_input_message, SNSMessageModel)
        message_type = cleaned_message['type']
        garage_name = cleaned_message['garage_name']

        response = {'id': message_id[:4], 'type': 'STATUS'}

        if message_type == 'STATUS':
            response['status'] = get_garage_dict_status(garage_name)
        elif message_type == 'CONTROL':
            response['status'] = [control_garage(garage_name, cleaned_message['action'])]
        else:
            response['status'] = [{'message': 'Invalid action passed', 'error': True}]

        # publish the message to the queue
        cleaned_response = json.dumps(marshal(response, GarageStatusResponseModel))
        app.logger.info("Publishing response: {}".format(cleaned_response))

        self._queue.send_message(MessageBody=cleaned_response)
