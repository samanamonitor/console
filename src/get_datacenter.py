#!/usr/bin/python

import json
import sys

# 'c04a22fe-dd01-4149-83c8-35cf7d3ec571'

class StatusData:
    def __init__(self, datacenter_uuid):
        try:
            fh = open("/var/lib/samanamonitor/" + datacenter_uuid, 'r')
            self.data = json.load(fh)
            fh.close()
        except:
            print "Invalid Datacenter"
            usage()

    def get_host(self, host_name):
        for host in self.data['hoststatus']:
            if host['host_name'] == host_name:
                return host
        return None

    def get_service(self, service_description, host_name):
        for service in self.data['servicestatus']:
            if service['service_description'] == service_description and service['host_name'] == host_name:
                return service
        return None

def usage():
    print "UNKNOWN - USAGE: loadhost_datacenter <datacenter-uuid> <service|host> <host_name> <service_description?>"
    exit(3)    

if len(sys.argv) < 4:
    print "Missing arguments"
    usage()

datacenter_uuid = sys.argv[1]
object_type = sys.argv[2]
if object_type != 'service' and object_type != 'host':
    print "Object type can only be service or host not \"%s\"" % object_type
    usage()

host_name = sys.argv[3]
if object_type == "service":
    if len(sys.argv) != 5:
        usage()
    service_description = sys.argv[4]

sd = StatusData(datacenter_uuid)
if object_type == 'host':
    h = sd.get_host(host_name)
    if h is None:
        plugin_output = "UNKNOWN - Host not found"
        performance_data = ""
        current_state = 3
    else:
        plugin_output = h['plugin_output']
        performance_data = h['performance_data']
        current_state = int(h['current_state'])

elif object_type == 'service':
    s = sd.get_service(service_description, host_name)
    if s is None:
        plugin_output = "UNKNOWN - Service not found"
        performance_data = ""
        current_state = 3
    else:
        plugin_output = s['plugin_output']
        performance_data = s['performance_data']
        current_state = int(s['current_state'])

print "%s | %s" % (plugin_output, performance_data)
exit(current_state)
