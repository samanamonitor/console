import sys
import requests
sys.path.insert(0, '.')
from samananag import StatusDat
import json


def usage():
    print "UNKNOWN - USAGE: uploaddata.py <datacenter-uuid> <url>"

print len(argv)
if len(sys.argv) != 2:
    usage()
    exit(3)

datacenter_uuid = sys.argv[0]
url = 'http://nagios.samanagroup.com/samanamonitor/datacenter/' + datacenter_uuid

s = StatusDat()
s.parse()
r = requests.put(url, data=json.dumps(s.data))

if r.status_code == requests.codes.ok:
    print "OK - Data Uploaded"
    exit(0)
else:
    print "CRITICAL - Unable to upload data"
    exit(2)
