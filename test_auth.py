import api
import os
import traceback
import random
import time
from collections import OrderedDict

# Export the following env variables:
# SERVER: https://api-internal.v3box1.mosip.net
# RESIDENT_CLIENT: mosip-resident-client
# RESIDENT_SECRET: xyz 

SCHEMA_VERSION = 0.1
def flatten_auth_response(r):
    '''
    r:  List of dicts containing each row
    '''
    table = OrderedDict()
    for k,v in r[0].items():  # first row 
        table[k] = []

    flattened = []
    # header row first
    for k in table:
        flattened.append(k)

    for row in r:
        for k,v in row.items():
            flattened.append(v)
    return flattened

def non_empty(a):
    if len(a.strip()) > 0: 
       return True
    else:
       return False
    
def filter_by_non_empty(d): # d: dict
    out = {}
    for k,v in d.items():
        if non_empty(v):
            out[k] = v
    return out

def create_identity_json(uin, fields):
   """
   Assumes string level validations have been performed on the fields before calling this func. No checks here.
   """
   iden = {
       'identity': {
           'IDSchemaVersion': SCHEMA_VERSION,
           'UIN': uin,
       }
   }
   fields = filter_by_non_empty(fields)
   if len(fields) == 0: 
     return None

   iden['identity'].update(fields)

   return iden

def get_rid_status(rid):
    server = os.environ['SERVER']
    try:
        token = api.auth_get_client_token(server, 'resident', os.environ['RESIDENT_CLIENT'], 
                                  os.environ['RESIDENT_SECRET'])
        status = api.get_rid_status(server, token, rid)
    except:
        formatted_lines = traceback.format_exc()
        print(formatted_lines)
        return 'EXCEPTION in code'
    return status

def get_credential_types():
    server = os.environ['SERVER']
    try:
        token = api.auth_get_client_token(server, 'resident', os.environ['RESIDENT_CLIENT'], 
                                  os.environ['RESIDENT_SECRET'])
        status = api.get_credential_types(server, token)
    except:
        formatted_lines = traceback.format_exc()
        print(formatted_lines)
        return 'EXCEPTION in code'
    return status

def req_otp(uin):
    server = os.environ['SERVER']
    txn_id  = str(random.randint(1000000000, 9999999999)) # Min digits required
    try:
        token = api.auth_get_client_token(server, 'resident', os.environ['RESIDENT_CLIENT'], 
                                  os.environ['RESIDENT_SECRET'])
        exit(0)
        status = api.req_otp(server, token, uin, txn_id)
        if status['errors'] is None:
            return True, 'OTP sent to your registered mobile and email', txn_id   # success
    except:
        formatted_lines = traceback.format_exc()
        print(formatted_lines)
        return False, 'EXCEPTION in code', txn_id
    return False, status, txn_id

def get_vid(uin, txn_id, otp):
    server = os.environ['SERVER']
    ok = False
    try:
        token = api.auth_get_client_token(server, 'resident', os.environ['RESIDENT_CLIENT'], 
                                  os.environ['RESIDENT_SECRET'])
        r = api.get_vid(server, token, uin, txn_id, otp)
        if len(r['errors']) == 0:
           return True, r['response']['vid'], r['response']['message']
    except:
        formatted_lines = traceback.format_exc()
        print(formatted_lines)
        return False, '', 'EXCEPTION in code'
    return False, '', str(r['errors'])

def update_uin(uin, txn_id, otp, fields):
    server = os.environ['SERVER']
    ok = False
    try:
        token = api.auth_get_client_token(server, 'resident', os.environ['RESIDENT_CLIENT'], 
                                  os.environ['RESIDENT_SECRET'])
        iden = create_identity_json(uin, fields)
        if iden is None:
            return False, 'No update fields entered'
        r = api.update_uin(server, token, uin, txn_id, otp, iden)
        # TODO: Return value should be RID that should be given to user
        #if len(r['errors']) == 0:
        #   return True, r['response']['vid'], r['response']['message']
        return True, 'Dummy success!'
    except:
        formatted_lines = traceback.format_exc()
        print(formatted_lines)
        return False, 'EXCEPTION in code'
    return False, str(r['errors'])

def get_auth_history(uin, txn_id, otp, nrecords):
    server = os.environ['SERVER']
    ok = False
    try:
        token = api.auth_get_client_token(server, 'resident', os.environ['RESIDENT_CLIENT'], 
                                  os.environ['RESIDENT_SECRET'])
        r = api.get_auth_history(server, token, uin, txn_id, otp, nrecords)
        if r['errors'] is None:
            return True, flatten_auth_response(r['response']['authHistory'])
    except:
        formatted_lines = traceback.format_exc()
        print(formatted_lines)
        return False, 'EXCEPTION in code'
    return False, str(r['errors'])

def auth_lock(uin, txn_id, otp, auth_types): 
    server = os.environ['SERVER']
    ok = False
    try:
        token = api.auth_get_client_token(server, 'resident', os.environ['RESIDENT_CLIENT'], 
                                  os.environ['RESIDENT_SECRET'])
        r = api.auth_lock(server, token, uin, txn_id, otp, auth_types)
        print(r)
        #if r['errors'] is None:
        #    return True 
    except:
        formatted_lines = traceback.format_exc()
        print(formatted_lines)
        return False, 'EXCEPTION in code'

    return False, str(r['errors'])

def auth_unlock(uin, txn_id, otp, auth_types, seconds): 
    server = os.environ['SERVER']
    ok = False
    try:
        token = api.auth_get_client_token(server, 'resident', os.environ['RESIDENT_CLIENT'], 
                                  os.environ['RESIDENT_SECRET'])
        r = api.auth_unlock(server, token, uin, txn_id, otp, auth_types, seconds)
        print(r)
        #if r['errors'] is None:
        #    return True 
    except:
        formatted_lines = traceback.format_exc()
        print(formatted_lines)
        return False, 'EXCEPTION in code'

    return False, str(r['errors'])


def main(argv):
   server=os.environ['SERVER']
   secret = os.environ['RESIDENT_SECRET']
   username = 'test_admin'
   user_password = 'mosip'

   try:
       for i in range(1, 10000):
           token = api.auth_get_client_token(server, 'resident', os.environ['RESIDENT_CLIENT'], secret)
           #token = api.auth_get_user_token(server, 'regproc', username, user_password)
           print(token)
           time.sleep(1)
   except:
        print(f'Failed at step {i}')
        formatted_lines = traceback.format_exc()
        print(formatted_lines)

   return 


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

