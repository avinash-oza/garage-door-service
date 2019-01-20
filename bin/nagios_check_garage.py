#!/usr/bin/env python
import sys
import requests
import argparse

# config is specified by env variable APP_SETTINGS
def check_garage(api_endpoint):
    resp = requests.get(api_endpoint)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        print("Exception when contacting API: {}".format(e))
        sys.exit(2)

    resp_dict = resp.json()
    status_text = "".join(["{} is {}.".format(k['garage_name'], k['status']) for k in resp_dict['status']])
    print(status_text)

    if any(k['error'] for k in resp_dict['status']) or any(k['status'] == 'OPEN' for k in resp_dict['status']):
        # exit with error code if any garage is open or error
        sys.exit(2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-endpoint', type=str, help="Garage status API endpoint")
    args = parser.parse_args()

    check_garage(args.api_endpoint)