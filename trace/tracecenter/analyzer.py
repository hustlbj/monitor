#!/usr/bin/env python

import os
import time
import multiprocessing
import signal
import pprint

from database import MongoDB
from detecting import Detecter
from common.logger import config_logging, getlogger
from include.configobj import ConfigObj


# Load configuration
root_dir = os.path.dirname(os.path.abspath(__file__)) + os.sep
CONF = ConfigObj(root_dir+"config")
config_logging(CONF['log_file'])

logger = getlogger('PerformanceAnalyzer')

class PerformanceAnalyzer(object):
    
    def __init__(self):
        db_addr = (CONF['db']['d_addr'],
                   CONF['db'].as_int('d_port'))
        db_name = CONF['db']['db']
        self.db = MongoDB(db_addr, db_name)
        self.worker_num = CONF['analyzer'].as_int('worker_num')
        self.ts = (-3600*24*30*5, None)
        self.queue = multiprocessing.Queue()


    def start(self):
        self.running = True
        self.tasks = []

        for i in range(self.worker_num):
            proc = multiprocessing.Process(target=self.worker, name="Worker-%d"%i)
            proc.start()
            self.tasks.append(proc)

    def worker(self):
        while True:
            job = self.queue.get()
            detecter = Detecter(job[0], job[1], self.ts, job[2])
            detecter.load_data()
            
            result = detecter.detect()
            result['path'] = job[0]
            result['func'] = job[1]
            result['from'] = detecter.tbegin
            result['to'] = detecter.tend
            
            logger.info('analyzer.worker: %s' % result['path']);
            self.db.insert_report(result)
	    # print analyzing result for each path
            pprint.pprint(result)


    def stop(self):
        self.running = False
        for task in self.tasks:
            task.terminate()

        for task in self.tasks:
            task.join()

        os._exit(0)

    def wait(self):
        
        while self.running:
            ret = self.db.get_paths()
            for item in ret:
                path = "%s-%s.%s" % (item['pack'], item['cls'], item['func'])

                ret = self.db.get_traces(path, self.ts)
                overview_len = 0
                overview_item = None
                for trace in ret:
                    if len(trace['overview'])>overview_len:
                        if trace.has_key('_id'):
                            trace.pop('_id')
                        overview_item = trace.pop('overview')
                        overview_len = len(overview_item)
                for item in overview_item:
                    job = (path, item['current'], overview_item)
                    self.queue.put(job)

            time.sleep(3600)


if __name__=="__main__":
    pa = PerformanceAnalyzer()
    pa.start()

    def _handler(a, b):
        pa.stop()

    signal.signal(signal.SIGINT, _handler)
    pa.wait()
