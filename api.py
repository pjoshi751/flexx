import requests
import datetime as dt
import traceback
import json
import base64

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
    if r['errors'] is not None:
        if len(r['errors']) > 0:
           code = r['errors'][0]['errorCode']
           msg = r['errors'][0]['message'] 
           return f'ERROR: {code}: {msg}'
    return r['response']['ridStatus']

def get_credential_types(server, token):
    url = f'''{server}/resident/v1/credential/types'''
    ts = get_timestamp()
    cookies = {'Authorization' : token}
    r = requests.get(url, cookies=cookies, verify=True)
    r = response_to_json(r)
    print(r)

def req_otp(server, token, uin, txn_id):
    url = f'''{server}/resident/v1/req/otp'''
    ts = get_timestamp()
    cookies = {'Authorization' : token}
    j = {    
        'id': 'mosip.identity.otp.internal',
        'version': '1.0',
        'transactionID': txn_id,
        'requestTime': ts,
        'individualId': uin,
        'individualIdType': 'UIN',
        'otpChannel': [
          'EMAIL'
        ],
        'metadata': {}
    }

    r = requests.post(url, cookies=cookies, json = j, verify=True)
    r = response_to_json(r)
    return r

def get_vid(server, token, uin, txn_id, otp):
    url = f'''{server}/resident/v1/vid'''
    ts = get_timestamp()
    cookies = {'Authorization' : token}
    j = {    
        'id': 'mosip.resident.vid',
        'version': 'v1',
        'requesttime': ts,
        'request': {
          'transactionID': txn_id,
          'individualId': uin,
          'individualIdType': 'UIN',
          'otp': otp,
          'vidType': 'Temporary'
        }
    }
    r = requests.post(url, cookies=cookies, json = j, verify=True)
    r = response_to_json(r)
    return r

def update_uin(server, token, uin, txn_id, otp, identity):
    """
    identity:  Json as idntity json with subset of fields - the ones that need to be changed.
    """
    url = f'''{server}/resident/v1/req/update-uin'''
    ts = get_timestamp()
    cookies = {'Authorization' : token}

    j = {    
        'id': 'mosip.resident.updateuin',
        'version': 'v1',
        'requesttime': ts,
        'request': {
          'transactionID': txn_id,
          'individualIdType': 'UIN',
          'individualId': uin,
          'otp': otp,
          'identityJson': base64.b64encode(json.dumps(identity).encode('utf-8')).decode()
        }
    }
    r = requests.post(url, cookies=cookies, json = j, verify=True)
    r = response_to_json(r)
    return r

def get_auth_history(server, token, uin, txn_id, otp, nrecords, start_page='1'):
    url = f'''{server}/resident/v1/req/auth-history'''
    ts = get_timestamp()
    cookies = {'Authorization' : token}
    j = {    
        'id': 'mosip.resident.authhistory',
        'version': 'v1',
        'requesttime': ts,
        'request': {
          'transactionID': txn_id,
          'individualId': uin,
          'otp': otp,
          'pageStart': start_page,
          'pageFetch': nrecords
        }
    }
    r = requests.post(url, cookies=cookies, json = j, verify=True)
    r = response_to_json(r)
    return r
    
def auth_lock(server, token, uin, txn_id, otp, auth_types):
    url = f'''{server}/resident/v1/req/auth-lock'''
    ts = get_timestamp()
    cookies = {'Authorization' : token}
    print('API:')
    print(auth_types)
    j = {    
        'id': 'mosip.resident.authlock',
        'version': 'v1',
        'requesttime': ts,
        'request': {
          'transactionID': txn_id,
          'individualId': uin,
          'individualIdType': 'UIN',
          'otp': otp,
          'authType': auth_types
        }
    }
    r = requests.post(url, cookies=cookies, json = j, verify=True)
    r = response_to_json(r)
    return r

def auth_unlock(server, token, uin, txn_id, otp, auth_types, seconds):
    url = f'''{server}/resident/v1/req/auth-unlock'''
    ts = get_timestamp()
    cookies = {'Authorization' : token}
    j = {    
        'id': 'mosip.resident.authlock',
        'version': 'v1',
        'requesttime': ts,
        'request': {
          'transactionID': txn_id,
          'individualId': uin,
          'individualIdType': 'UIN',
          'otp': otp,
          'authType': auth_types,
          'unlockForSeconds': str(seconds)
        }
    }
    r = requests.post(url, cookies=cookies, json = j, verify=True)
    r = response_to_json(r)
    return r
