import sys
import requests
sys.path.insert(0, '.')
from samananag import StatusDat

datacenter_uuid = 'asdfa'
url = 'http://nagios.samanagroup.com/samanamonitor/datacenter/' + datacenter_uuid

s = StatusDat()
s.parse()
r = requests.put(url, data=json.dumps(s.data))

if r.status_code == requests.code.ok:
    print "OK - Data Uploaded"
    exit(0)
else:
    print "CRITICAL - Unable to upload data"
    exit(2)
