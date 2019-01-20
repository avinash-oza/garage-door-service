#!/usr/bin/env python
import sys
import requests
import argparse

# config is specified by env variable APP_SETTINGS
def check_garage(api_endpoint):
    resp = requests.get(api_endpoint)
    exit_code = 0
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        status_text = "Exception when contacting API: {}".format(e)
        exit_code = 2
        return status_text, exit_code

    resp_dict = resp.json()
    status_text = "".join(["{} is {}.".format(k['garage_name'], k['status']) for k in resp_dict['status']])

    if any(k['error'] for k in resp_dict['status']) or any(k['status'] == 'OPEN' for k in resp_dict['status']):
        # exit with error code if any garage is open or error
        exit_code = 2
    return status_text, exit_code

def submit_check(api_endpoint, passive_check_endpoint, token, hostname):
    status_text, exit_code = check_garage(api_endpoint)
    submit_cmd = "PROCESS_SERVICE_CHECK_RESULT;{};Garage Status;{};{}".format(hostname, exit_code, status_text)
    resp = requests.get(passive_check_endpoint, params={'token': token,
                                                        'cmd': 'submitcmd',
                                                        'command': submit_cmd})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-endpoint', type=str, help="Garage status API endpoint")
    parser.add_argument('--token', type=str, help="Nagios passive check token")
    parser.add_argument('--submit-check-url', type=str, help="Nagios passive check url")
    args = parser.parse_args()

    submit_check(args.api_endpoint, args.submit_check_url, args.token)