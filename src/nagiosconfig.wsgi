import json
from pynag import Model
from urlparse import parse_qs

def get_host(host_name=None):
    if host_name is None:
        return [ '501 Invalid Input', "ERROR: No host_name" ]

    h = Model.Host.objects.filter(host_name=host_name)
    if len(h) == 0:
        return [ '501 Invalid Input', "ERROR: Invalid host_name" ]

    return [ '200 OK', json.dumps(h[0]) ]

def host_list(registered=None,in_hostgroup=""):
    hl = []
    for h in Model.Host.objects.filter(register=registered,hostgroups__regex=r"\b"+in_hostgroup+r"\b"):
        hl += [ h.get("host_name", None) ]
    return [ '200 OK', json.dumps(hl) ]

def hostgroup_list(registered=None):
    hgl = []
    for hg in Model.Hostgroup.objects.filter(register=registered):
        hgl += [ hg.get("hostgroup_name", None) ]
    return [ '200 OK', json.dumps(hgl) ]

def service_status(host_name=None, service_description=None):
    if host_name is None or service_description is None:
        return [ '501 Invalid Input', "ERROR: No host_name or service_description" ]
    svcs = Model.Service.objects.filter(service_description=service_description)
    if len(svcs) == 0:
        return [ '501 Invalid Input', "ERROR: Invalid service_description" ]
    h = Model.Host.objects.filter(host_name=host_name)
    if len(h) == 0:
        return [ '501 Invalid Input', "ERROR: Invalid host_name" ]
    svcs[0].host_name = host_name
    status = svcs[0].get_current_status()
    return [ '200 OK', json.dumps(status) ]

def application(environ, start_response):
    status = '200 OK'
    query = parse_qs(environ['QUERY_STRING'])

    action = query.get('action', ['none'])[0]
    q_host = query.get('host', ['none'])[0]
    registered = query.get('registered', ['1'])[0]
    in_hostgroup = query.get('in_hostgroup', [""])[0]
    service_description = query.get('service_description', [None])[0]

    output = json.dumps(query, indent=2)
    
    if action == 'get_host':
        [status, output] = get_host(q_host)

    elif action == 'host_list':
        [status, output] = host_list(registered, in_hostgroup)

    elif action == 'hostgroup_list':
        [status, output] = hostgroup_list(registered)

    elif action == 'service_status':
        [status, output] = service_status(q_host, service_description)

    elif action == 'none':
        [status, output] = ['501 Invalid Input', "ERROR: Invalid action" ]

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [ output ]
