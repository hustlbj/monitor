#!/usr/bin/env python

import os.path as path
import json
import zlib

import database

from include.configobj import ConfigObj

# Load configuration
root_dir = path.dirname(path.abspath(__file__)) + path.sep
CONF = ConfigObj(root_dir+"config")


def jsonize(func):
    """
    Decorate function to ensure result with json format.
    """

    def post(*args, **kargs):
        ret = func(*args, **kargs)
        return json.dumps(ret)

    post.__name__ = func.__name__
    return post


class API(object):
    """
    """

    def __init__(self):
        conf = CONF['db']
        self.db = database.MongoDB((conf['d_addr'], conf.as_int('d_port')), conf['db'])


    def get_traces(self, api, overview=True, start=None, end=None):
        """
        """
        if not (start or end):
            ts = None
        elif start < 0:
            ts = (start, None)
        elif start and end and start < end:
            ts = (start, end)
        else:
            return [False, 'wrong start and end']

	# database.py  MongoDB.get_traces(collection, time_section)
	# print "get_traces:", api, ts
        ret = self.db.get_traces(api, ts)
        overview_len = 0
        overview_item = None
        for trace in ret:
            if len(trace['overview'])>overview_len:
                if trace.has_key('_id'):
                    trace.pop('_id')
                overview_item = trace.pop('overview')
                overview_len = len(overview_item)

            if trace['category']=='normal':
                trace['cost'] = (trace['trace'][0]['end']-trace['trace'][0]['start'])*1000

            for entry in trace['trace']:
		entry.pop('start')
		try:
                    entry.pop('end')
                except Exception, e:
                    pass

        if overview:
            return [True, ret, overview_item]
        else:
            return [True, ret]

    
    def get_general_traces(self):
        """
        """

        try:
            ret = self.db.get_paths()
        except Exception, e:
            return [False, str(e)]

        return [True, ret]

    def get_report(self, path, func):
        try:
            ret = self.db.get_report(path, func)
        except Exception, e:
            return [False, str(e)]

        return [True, ret]
       
    def get_path_report(self, path):
        try:
            ret = self.db.get_path_report(path)
        except Exception, e:
            return [False, str(e)]

        return [True, ret]


api = API()

if __name__=="__main__":
    import pprint
    #print api.get_general_traces()
    #pprint.pprint(api.get_traces('IaaSAPI-IaaSAPI.get_vmpool_info', start=-3600))
    #print api.get_report('IaaSAPI-IaaSAPI.get_vmpool_info', 'IaaSOperation-IaaSOperation.get_vmpool_info')
    #print api.get_path_report('IaaSAPI-IaaSAPI.get_vmpool_info')
    print api.get_general_traces()
    #print api.get_traces('iaas_handler-IaaSHandler.get_hostpool_info')
