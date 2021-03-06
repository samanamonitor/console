#!/usr/bin/python

import json
from pymongo import MongoClient
import sys

# 'c04a22fe-dd01-4149-83c8-35cf7d3ec571'

class StatusData:
    def __init__(self, datacenter_uuid):
        client = MongoClient()
        self.db = client[datacenter_uuid]

    def find(self, collection, f=None):
        return self.db[collection].find(f)

    def find_one(self, collection, f=None):
        result = self.find(collection, f)
        if result.count() != 1:
            return None
        else:
            return result[0]

    def get_host(self, host_name):
        f = {"host_name": host_name}
        return self.find_one('hoststatus', f)

    def get_service(self, service_description, host_name):
        f = { "host_name": host_name, "service_description": service_description }
        return self.find_one("servicestatus", f)

    def get_service_for_host(self, host_name):
        f = { "host_name": host_name }
        services = []
        for s in self.find("servicestatus", f):
            services += [ s['service_description'] ]
        return services

    def get_hosts(self):
        hs = []
        for host in self.find('hoststatus'):
            hs += [ host['host_name'] ]
        return hs

    def get_host_config_all(self):
        config = ""
        for host_name in self.get_hosts():
            if host_name == 'localhost': continue
            config += """define host {
            use                    samana-host
            host_name              %s
            }\n\n""" % host_name
        return config

    def sd_get_service_config_all(self):
        config = ""
        for service in self.find('servicestatus'):
            if service['host_name'] == 'localhost': continue
            config += """define service {
            use                    samana-service
            host_name              %s
            service_description    %s
            }\n\n""" % (service['host_name'], service['service_description'])
        return config

def usage():
    print "UNKNOWN - USAGE: loadhost_datacenter <datacenter-uuid> <service|host|hostservices|hosts> <host_name?> <service_description?>"
    exit(3)    

argc = len(sys.argv)

if argc < 3:
    print "Missing arguments"
    usage()

datacenter_uuid = sys.argv[1]
object_type = sys.argv[2]

if object_type == 'service':
    if argc != 5: usage()
    host_name = sys.argv[3]
    service_description = sys.argv[4]

elif object_type == 'host':
    if argc != 4: usage()
    host_name = sys.argv[3]

elif object_type == 'hostservices':
    if argc != 4: usage()
    host_name = sys.argv[3]

elif object_type == 'hosts':
    pass

elif object_type == 'host_config_all':
    pass

elif object_type == 'service_config_all':
    pass

else:
    print "Invalid object type"
    usage()


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

elif object_type == 'hostservices':
    print sd.get_service_for_host(host_name)
    exit(0)

elif object_type == 'hosts':
    print sd.get_hosts()
    exit(0)

elif object_type == 'host_config_all':
    print sd.get_host_config_all()
    exit(0)

elif object_type == 'service_config_all':
    print sd.sd_get_service_config_all()
    exit(0)

print "%s | %s" % (plugin_output, performance_data)
exit(current_state)
