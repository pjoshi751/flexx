import requests
import datetime as dt
import traceback
import json

def get_timestamp(seconds_offset=None):
    '''
    Current TS.
    Format: 2019-02-14T12:40:59.768Z  (UTC)
    '''
    delta = dt.timedelta(days=0)
    if seconds_offset is not None:
        delta = dt.timedelta(seconds=seconds_offset)

    ts = dt.datetime.utcnow() + delta
    ms = ts.strftime('%f')[0:3]
    s = ts.strftime('%Y-%m-%dT%H:%M:%S') + '.%sZ' % ms
    return s

def response_to_json(r):
    try:
        #myprint('Response: <%d>' % r.status_code)
        r = r.content.decode() # to str 
        r = json.loads(r)
    except:
        r = traceback.format_exc()
    return r

def read_token(response):
    cookies = response.headers['Set-Cookie'].split(';')
    for cookie in cookies:
        key = cookie.split('=')[0]
        value = cookie.split('=')[1]
        if key == 'Authorization':
            return value
    return None

def auth_get_client_token(server, appid, clientid, secret):
    '''
        server: full url of the server like https://api-internal.sandbox.mosip.net
    '''
    url = f'''{server}/v1/authmanager/authenticate/clientidsecretkey'''
    ts = get_timestamp()
    j = {
        'id': 'string',
        'metadata': {},
        'request': {
            'appId': appid,
            'clientId': clientid,
            'secretKey': secret
        },
        'requesttime': ts,
        'version': '1.0'
    }

    r = requests.post(url, json = j, verify=True)
    token = read_token(r)
    return token

def get_rid_status(server, token, rid):
    url = f'''{server}/resident/v1/rid/check-status'''
    ts = get_timestamp()
    cookies = {'Authorization' : token}
    j = {
        'id': 'mosip.resident.checkstatus',
        'version': 'v1',
        'requesttime': ts,
        'request': {
        'individualId': rid,
        'individualIdType': 'rid'
        } 
    }

    r = requests.post(url, cookies=cookies, json = j, verify=True)
    r = response_to_json(r)
    return r['response']['ridStatus']

