import datetime

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
            response['message'] = 'TRIGGERED {0} GARAGE TO {1}. OLD POSITION: {2}'.format(garage_name, action,
                                                                                          current_garage_status)

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
