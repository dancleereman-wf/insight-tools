#!/usr/bin/python

import base64
import datetime
import json
import sys
import time

import requests

from settings import INSIGHT_STAGING_BASE_URL, INCOMING_KINESIS_ERRORS_PATH, \
    LOCAL_COOKIE, STAGING_COOKIE, PROCESS_ERRORS_PATH


def main():
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    if sys.argv[1] == '-l' or sys.argv[1] == '--local':
        base_url = 'http://localhost:8080'
    else:
        base_url = INSIGHT_STAGING_BASE_URL

    service = sys.argv[2]
    now = datetime.datetime.now()
    _time = now.strftime('%Y/%m/%d %H:%M:%S')
    message = 'testing'

    log = {
        "context": {},
        "exception": {},
        "level": "",
        "message": message,
        "metadata": {},
        "service": service,
        "time": _time,
        "version": ""
    }

    encoded_data = base64.b64encode(json.dumps(log))
    raw_body = {'data': [encoded_data]}
    encoded_body = json.dumps(raw_body)

    url = create_url(base_url, INCOMING_KINESIS_ERRORS_PATH)

    headers = {
        'Content-Type': 'application/json',
    }

    cookies = {
        "dev_appserver_login": LOCAL_COOKIE,
        "SACSID": STAGING_COOKIE
    }

    # kick off process errors if local
    if sys.argv[1] == '-l' or sys.argv[1] == '--local':
        r = requests.get(base_url + PROCESS_ERRORS_PATH, cookies=cookies)
        time.sleep(10)

        if r.status_code != 200:
            print 'An error has occurred. Status code: ' + str(r.status_code)
            sys.exit(1)
        else:
            print 'Success! Status code: ' + str(r.status_code)

    # simulate kinesis error
    r = requests.post(url, headers=headers, data=encoded_body, cookies=cookies)

    if r.status_code != 200:
        print 'An error has occurred. Status code: ' + str(r.status_code)
        sys.exit(1)
    else:
        print 'Success! Status code: ' + str(r.status_code)


def create_url(base, path, params=None):
    if not params:
        return base + path
    else:
        url = base + path + '?'
        for key, value in params.iteritems():
            url += key + '=' + str(value) + '&'
        return url


def usage():
    print 'usage: simulate_gcp_error.py [-l | --local][-s | --staging] [project]'


if __name__ == '__main__':
    main()
