#!/usr/bin/env python

import json
import time
import pprint
from api import API, cloud

def test_vm():
    vms = json.loads(cloud.get_vms_info(template=0))[1]
    
    report = {'normal':[], 'failed':[]}
    for vm in vms:
        ret = API.get_stats(vm['guid'], 'bytes_in')
        if ret[0] and len(ret[1]):
            report['normal'].append([vm['guid'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ret[1][0][0]))])
        else:
            report['failed'].append([vm['guid'], vm['ip']])
        time.sleep(0.5)
    pprint.pprint(report)
    return report

if __name__=="__main__":
    test_vm()
