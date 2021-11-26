from api import *
import os


SERVER=os.environ['SERVER']

token = auth_get_client_token(SERVER, 'resident', os.environ['RESIDENT_CLIENT'], 
                              os.environ['RESIDENT_SECRET'])
status = get_rid_status(SERVER, token, '10002100000000220211103111458')
print(status)
