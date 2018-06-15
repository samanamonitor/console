#!/usr/bin/python

import json
import sys

# 'c04a22fe-dd01-4149-83c8-35cf7d3ec571'

class StatusData:
    def __init__(self, datacenter_uuid):
        fh = open("/var/lib/samanamonitor/" + datacenter_uuid, 'r')
        self.data = json.load(fh)
        fh.close()

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


if len(sys.argv) != 2:
    print "UNKNOWN - USAGE: loadhost_datacenter <datacenter-uuid> <host_name>"
    exit(3)

datacenter_uuid = sys.argv[1]
host_name = sys.argv[2]

sd = StatusData(datacenter_uuid)
h = sd.get_host(host_name)
if h is not None:
    print json.dumps(h, indent=2)
else:
    print "UNKNOWN - No Host"