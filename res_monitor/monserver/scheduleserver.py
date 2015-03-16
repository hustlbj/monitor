#!/usr/bin/env python

import threading
#import time
#import sys
#import errno
import os
#import socket
import os.path as path
import pymongo
import json

#from database import MongoDB
from include.configobj import ConfigObj
from common.sockcontext import PollContext
#from common.package import Package
from common.logger import config_logging, getlogger

root_dir = path.dirname(path.abspath(__file__)) + path.sep
CONF = ConfigObj(root_dir + "schedule.conf")
config_logging(CONF['log_file'])
logger = getlogger('SchedServer')


class SchedServer():

    def __init__(self):
        self.event = threading.Event()
        self.conf_db = (CONF['db']['addr'], CONF['db'].as_int('port'), \
                        CONF['db']['db'], CONF['db']['meta_collection'])
        self.conf_collector = (CONF['collector']['addr'], \
                                CONF['collector'].as_int('port'), \
                                CONF['collector'].as_int('interval'))


    @property
    def running(self):
        return not self.event.isSet()


    def collect(self):
        context = PollContext((self.conf_collector[0], self.conf_collector[1]))
        context.initialize()
        interval = self.conf_collector[2]
        logger.info("Schedule collector is running.")
        while self.running:
            try:
                events = context.wait(1000)
                for event, data, sock in events:
                    if event == "SCHE":
                        '''
                        data_dict = eval(data.replace('[', 'list(').\
                                        replace(']', ')').\
                                        replace('{', 'dict(').\
                                        replace('}', ')').\
                                        replace(':', '='))
                        '''
                        data_dict = json.loads(data)
                        #data_dict = eval(data)
                        logger.info("Get data from %s, %s" % \
                                    (data_dict['from'], data_dict['day']))
                        self.store(data_dict['from'], {'day': data_dict['day'],\
                                    'statistics': data_dict['value']})
                        #self.store(self.conf_db[3], self.get_statistics(data_dict))
                        logger.info("Store %s's statistics." % data_dict['from'])
            except Exception, e:
                logger.error(str(e))


    def store(self, db, data):
        try:
            conn = pymongo.Connection(self.conf_db[0], self.conf_db[1])
            for host in data['statistics']:
                if host['type'] == 'physical':
                    col = conn[db]["p_" + host['name']]
                else:
                    col = conn[db]["v_" + host['name']]
                col.insert({'day': data['day'], 'value': host['value']})
        except Exception, e:
            logger.error(str(e))


    def get_statistics(self, data):
        p_num = 0
        v_num = 0
        for value in data['value']:
            if value['type'] == 'physical':
                p_num += 1
            else:
                v_num += 1
        statistics = {'name': data['from'], 'day': data['day'], \
                        'p_nums': p_num, 'v_num': v_num}
        pass


    def start(self):
        logger.info("Starting Schedule Server: pid %d" % os.getpid())
        self.event.clear()
        self.collect()


    def wait(self):
        pass


    def stop(self):
        self.event.set()
        logger.info("Closing Schedule Server.")


if __name__ == '__main__':
    sched = SchedServer()
    sched.start()