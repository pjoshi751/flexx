import api
import os
import traceback
import random

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

