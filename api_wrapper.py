import api
import os
import traceback

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

