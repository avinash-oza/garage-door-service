import datetime
import json

import boto3
import requests
from flask import request
from flask_restplus import Resource, fields, marshal

from garage_door.pi_funcs import trigger_garage, get_garage_status, SORTED_KEYS


def value_to_status(value):
    """
    returns the position given a number
    :param value:
    :return:
    """
    return 'CLOSED' if value == 0 else 'OPEN'


def control_garage(garage_name, action):
    response = {'garage_name': garage_name, 'error': True}

    # Check what the current location is
    current_garage_status = value_to_status(get_garage_status(garage_name))
    response['status'] = current_garage_status
    if current_garage_status == 'OPEN' and action == 'OPEN':
        response['message'] = 'Trying to open garage that is already open'
    elif current_garage_status == 'CLOSED' and action == 'CLOSE':
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
            # Nagios fields
            one_response['plugin_output'] = "Garage is {0}".format(garage_status)
            one_response['service_description'] = "{0} Garage Status".format(one_garage.capitalize())
            one_response['hostname'] = app.config['GENERAL_HOSTNAME']
            one_response['return_code'] = "0" if garage_status == "CLOSED" else "2"
            one_response['status'] = 'OPEN' if garage_status == OPEN else 'CLOSED'

        one_response['garage_name'] = one_garage
        one_response['status_time'] = datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')

        response.append(one_response)

    return response

# web related logic

GarageStatusModel = api.model('GarageStatusModel', {
    'garage_name': fields.String(),
    'status': fields.String(),
    'error': fields.Boolean(),
    'message': fields.String(allow_null=True)
})
NagiosGarageStatusModel = api.inherit('NagiosGarageStatusModel', GarageStatusModel,
                                      {'return_code': fields.String(),
                                       'plugin_output': fields.String(),
                                       'status_time': fields.String(),
                                       'service_description': fields.String()
                                       }
                                      )
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
            print(e)
            print("exception parsing {}".format(request.data))
        else:
            if data['Type'] == 'SubscriptionConfirmation' and 'SubscribeURL' in data:
                # call the subscription url to confirm
                print(data['SubscribeURL'])
                requests.get(data['SubscribeURL'])
            elif data['Type'] == 'Notification':
                # extract out the message and process
                print("Message is {}".format(data))
                self.process_sns_message(data)
            else:
                print("Couldnt process message: {}".format(data))

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
        cleaned_response = marshal(response, GarageStatusResponseModel)
        print("TEST publishing {}".format(json.dumps(cleaned_response)))

        # self._queue.send_message(MessageBody=json.dumps(response))
