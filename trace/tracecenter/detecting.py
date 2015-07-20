#!/usr/bin/env python
#coding:utf-8

import time
import os
import pprint

from database import MongoDB
from cluster import KmeansCluster
from include.configobj import ConfigObj
from common.logger import config_logging, getlogger


# Load configuration
root_dir = os.path.dirname(os.path.abspath(__file__)) + os.sep
CONF = ConfigObj(root_dir+"config")
config_logging(CONF['log_file'])
logger = getlogger('Detector')


class Detecter(object):
    def __init__(self, path_name, comp_name, time_section, overview):
        self.path = path_name
        self.comp = comp_name
        self.ts = time_section
        self.overview = overview
        db_conf = CONF['db']
        self.db = MongoDB((db_conf['d_addr'], db_conf.as_int('d_port')), db_conf['db'])
        self.data = []
        self.max = 0
        self.min = 100000
        self.vola = CONF['detect'].as_float('vola')
        self.min_k = CONF['detect'].as_int('min_k')
        self.max_k = CONF['detect'].as_int('max_k')


    def load_data(self):
        data = self.db.get_traces(self.path, self.ts)
        self.tbegin = time.time()
        self.tend = 0.0
        for trace in data:
            trace_id = trace['id']
	    # modified by LBJ
            #if trace['category']!='normal':
            if trace['category']=='failed':
                continue

            if trace['overview']!=self.overview:
                continue

            if trace['time']<self.tbegin:
                self.tbegin = trace['time']
            if trace['time']>self.tend:
                self.tend = trace['time']

            for item in trace['trace']:
                if item['current']==self.comp:
                    self.max = item['cost'] if self.max<item['cost'] else self.max
                    self.min = item['cost'] if self.min>item['cost'] else self.min
                    self.data.append({'id':trace_id, 'cost':item['cost']})


    @property
    def _k(self):
        if self.max<1:
            return 1

        if self.vola<1:
            self.swing = self.min*(2*self.vola)/(1-self.vola)
            k = int((self.max-self.min)/self.swing)+1

        if k < self.min_k:
            k = self.min_k 

        if k > len(self.data):
            k = 2

        if k > len(self.data):
            k = 1

        if k > self.max_k:
            k = self.max_k 

        return k

    def detect(self):
        if not len(self.data):
            return {}

        kmeans = KmeansCluster(self.data, self._k, ['cost'])
        kmeans.initialize()
        kmeans.cluster()

        clusters = sorted(kmeans.clusters, cmp=lambda x,y:cmp(x.centroid['cost'], y.centroid['cost']))
       
        fixed_clusters = []
        while len(clusters)>1:
            first = clusters.pop(0)
            second = clusters.pop(0)
            if first.distance(second) < self.swing:
                first.merge(second)
            else:
                fixed_clusters.append(first)
                first = second
            clusters = [first] + clusters
            kmeans.clusters = clusters
            kmeans.cluster()
            clusters = sorted(kmeans.clusters, cmp=lambda x,y:cmp(x.centroid['cost'], y.centroid['cost']))

        clusters = fixed_clusters + clusters

        return self._report(clusters)


    def _report(self, clusters):
        result = {}
        normal = clusters.pop(0)
        
        result['normal'] = {'size':len(normal.points), 'val':normal.centroid['cost']}
        total = 0
        for i, cluster in enumerate(clusters):
            name = "anomaly-%d" % i
            result[name] = {'size': len(cluster.points), 
                            'val': cluster.centroid['cost'],
                            'instances': cluster.points}
	    # modified by LBJ
            logger.info('found anomaly, call db.set_traces_abnormal')
            self.db.set_traces_abnormal(self.path, result[name]['instances']);	

            total += result[name]['size']

        result['anomaly'] = total
        result['total'] = total+result['normal']['size']

        return result
                            
                         
if __name__=="__main__":
    d = Detecter("IaaSAPI-IaaSAPI.get_vmpool_info", "net_attach-query_ipv6", (-3600*24*30, None))
    d.load_data()
    print len(d.data)
    pprint.pprint(d.detect())
    print d.tbegin
    print d.tend
