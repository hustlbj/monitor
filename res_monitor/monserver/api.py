#!/usr/bin/env python
import os.path as path
import json

from include.craneQueue.proxy import RPCProxy
from include.configobj import ConfigObj

curdir = path.dirname(path.abspath(__file__))
CONF = ConfigObj(curdir+path.sep+'server.conf')

import IaaSAPI

conf={}
conf["DIRECT_EXCHANGE"] = "call_direct_topic"
conf["TOPIC_EXCHANGE"] = "service_call_topic"
conf["RPC_EXCHANGE"] = "service_cast_topic"

cloud = IaaSAPI.IaaSAPI(conf, 'iaas_api')

class MonitorAPI(RPCProxy):
    def __init__(self, config, service):
        conf = CONF['register']
        super(MonitorAPI, self).__init__(config, service, host=conf['r_addr'])

    def get_stats(self, hostId, metricName, stat="AVERAGE", step=60, \
                   startTime=None, endTime=None):
        ret =  self.call(self.make_msg('get_stats', host=hostId, metric=metricName, strategy=stat, step=step, \
                   start=startTime, end=endTime), 'get_stats') 
	return json.loads(ret)

    def get_host_info(self, hostId):
	ret = self.call(self.make_msg('get_host_info', host=hostId), 'get_host_info')
	return json.loads(ret)

    def get_host_list(self):
        ret = self.call(self.make_msg('get_host_list'), 'get_host_list')
	return json.loads(ret)

    def get_metric_list(self, hostId):
        ret = self.call(self.make_msg('get_metric_list', host=hostId), 'get_metric_list')
	return json.loads(ret)

    def remove_host(self, host_list):
        ret = self.call(self.make_msg('remove_host', host_list=host_list), 'remove_host')
	return json.loads(ret)

    def get_metric_description(self):
        ret = self.call(self.make_msg('get_metric_description'), 'get_metric_description')
	return json.loads(ret)

    def dump_metric(self, start=None, end=None):
        ret = self.call(self.make_msg('dump_metric', start=start, end=end), 'dump_metric', timeout=120)
	return json.loads(ret)

    def get_single_node_info(self):
        hostpool = json.loads(cloud.get_hostpool_info())
        if not hostpool[0]:
            return [False, {'Status':'OFF'}]

        hostpool = hostpool[1]
        user_info = json.loads(cloud.get_user_list())
        users = len(user_info[1])

        cputotal = 0
        cpuused = 0
        memtotal = 0
        memfree = 0
        disktotal = 0
        jobsrunning = 0
        hosts = 0

        for host in hostpool:
            if host['state'] in [0, 2]:
                hosts += 1
                cputotal += int(host["totalCpu"])
                cpuused += int(host["usedCpu"])
                memtotal += int(host["totalMemory"])
                memfree += int(host["freeMemory"])
                jobsrunning += int(host["virtualMachines"])
                hostinfo = self.get_host_info(host["name"])
                if hostinfo[0]:
                     for disk in hostinfo[1]["disks"].values():
                          disktotal += int(disk["size"])

        result = {
            'Status': 'ON',
            'Hosts': hosts,
            'ComputeCap': '',
            'CPUTotal': cputotal,
            'CPUUsed': cpuused,
            'MemTotal': memtotal,
            'MemUsed': memtotal-memfree,
            'DiskTotal': disktotal,
            'UsersTotal': users,
            'JobsRunning': jobsrunning
        }

        return [True, result]


API = MonitorAPI(conf, 'monitorapi')

if __name__=="__main__":
    print API.get_host_list()
    #print API.dump_metric(-30)
    print API.get_stats('3761', 'bytes_in')
    #print API.get_single_node_info()
