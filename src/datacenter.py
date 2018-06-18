import json
import os.path
import sys
from time import time
from pymongo import MongoClient

def res_forbidden(environ, message=None):
    if message is None:
        message = "You don't have permission to access %s on this server." % environ['SCRIPT_NAME']
    status = '403 Forbidden'
    html = json.dumps({ 'result': 'Error', 'data': message})
    content_type = 'text/x-json'
    return (status, html, content_type)

def res_error(environ, message=None):
    if message is None:
        message = "The server encountered an internal error or misconfiguration and was unable to complete your request."
    status = '500 Internal Server Error'
    html = json.dumps({ 'result': 'Error', 'data': message})
    content_type = 'text/x-json'
    return (status, html, content_type)

def application(environ, start_response):
    content_type = 'text/x-json'
    datacenter_uuid = environ['PATH_INFO'].split('/')[1]

    if environ['REQUEST_METHOD'] != 'PUT':
        (status, output, content_type) = res_forbidden(environ)
    elif datacenter_uuid == '':
        (status, output, content_type) = res_forbidden(environ, 
            "Datacenter %s not defined" % datacenter_uuid)
    # TODO: elif not authenticated(dcuuid, envinron['HTTP_Authentication'])
    else:
        status = '200 OK'
        try:
            dcdata = json.load(environ['wsgi.input'])
            client = MongoClient()
            client.drop_database(datacenter_uuid)
            db = client[datacenter_uuid]
            for collection in data:
                db[collection].insert(dcdata[collection])
            output = json.dumps({ 'result': 'OK', 'data_size': environ['CONTENT_LENGTH']})
        except:
            print >> environ['wsgi.errors'], sys.exc_info()[1]
            (status, output, content_type) = res_error(environ, "See server log for details.")

    response_headers = [('Content-type', content_type),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [ output ]