#!/usr/bin/env python
#coding=utf-8
import socket
import time
import pprint
import os
import multiprocessing
import pymongo

from structure import Trace,TIMEOUT, DELAY
from database import MongoDB
from common.logger import config_logging, getlogger
from common.sockcontext import PollContext
from include.configobj import ConfigObj

# Load configuration
root_dir = os.path.dirname(os.path.abspath(__file__)) + os.sep
CONF = ConfigObj(root_dir+"config")
config_logging(CONF['log_file'])

logger = getlogger('TraceCenter')


class TraceCenter(object):
    
    def __init__(self):
        self.sock_addr = (CONF['collector']['c_addr'], 
                          CONF['collector'].as_int('c_port'))
        db_addr = (CONF['db']['d_addr'],
                        CONF['db'].as_int('d_port'))
        db_name = CONF['db']['db']
        self.db = MongoDB(db_addr, db_name)

        self.manager = multiprocessing.Manager()
        self.traces = self.manager.dict()
        self.trace_lock = multiprocessing.Lock()
        self.queue = multiprocessing.Queue()
        self.tasks = []


    def start(self):
        collector_proc = multiprocessing.Process(target=self.collector, name="Collector")
        collector_proc.start()
        self.tasks.append(collector_proc)

        analyzer_proc = multiprocessing.Process(target=self.analyzer, name="Analyzer")
        analyzer_proc.start()
        self.tasks.append(analyzer_proc)



    def collector(self):

        context = PollContext(self.sock_addr)
        context.initialize()

        while True:

            events = context.wait(1000)
     
            for event, data, sock in events:
                if event == "DATA":
                    entrys = eval(data) 

                    for entry in entrys:
                        trace_id = entry['trace']
            
                        if not self.traces.has_key(trace_id):
                            with self.trace_lock:
                                self.traces[trace_id] = Trace(entry)
				print 'new:', self.traces[trace_id]
            
                        elif not entry.has_key('end') and not entry.has_key('state'):
                            with self.trace_lock:
                                trace = self.traces[trace_id]
                                trace.add(entry)
                                self.traces[trace_id] = trace 
				print 'add:', self.traces[trace_id]
                        else:
                            with self.trace_lock:
                                trace = self.traces[trace_id]
                                trace.complement(entry)
                                self.traces[trace_id] = trace 
				print 'complete:', self.traces[trace_id]
            
#                                if trace.is_complete:
#                                #    self.traces.pop(trace_id)
#                                    self.queue.put((trace_id, trace.trace[0]['start']))
                


    def analyzer(self):

        while True:
            entry_list = {}
            now = time.time()
            for id, trace in self.traces.items():

                trace_start = trace.trace[0]['start']
                if now - trace_start > TIMEOUT:
                    category = 'timeout'
                elif now - trace_start > DELAY and trace.is_complete:
                    # trace链路不合法
                    if not trace.is_valid():
                        with self.trace_lock:
                           try:
                               self.traces.pop(id)
                           except KeyError, e:
                               pass
                        logger.info( "ABORD %s %s" % (time.strftime("%c", time.localtime(trace.trace[0]['start'])), 
                                                      id))
                        continue
                       
                    if trace.is_failed:
                        category = 'failed'
                    else:
                        category = 'normal'
                else:
                    continue

                with self.trace_lock:
                    try:
                        self.traces.pop(id)
                    except KeyError, e:
                        continue

                trace.sort()
                trace.format()
                
                entry = {'id': trace.id, 
                         'time':trace.time, 
                         'trace': trace.trace, 
                         'overview': trace.overview, 
                         'category': category}
                if not entry_list.has_key(trace.key):
                    entry_list[trace.key] = [entry]
                else:
                    entry_list[trace.key].append(entry)

                pprint.pprint(entry)
                logger.info( "%s [ %s ] %s %s" % (category.upper(), 
                                                  trace.key, 
                                                  time.strftime("%c", time.localtime(trace.time)), 
                                                  trace.id) )

     
            self.db.insert_traces(entry_list)
                
            time.sleep(1)


    def stop(self):
        self.manager.shutdown()

        for task in self.tasks:
            task.terminate()

        for task in self.tasks:
            task.join()

        os._exit(0)


    def wait(self):
        while True:
            time.sleep(60)


if __name__=="__main__":
    import signal

    tw = TraceCenter()
    tw.start()
    
    def _handler(a, b):
        tw.stop()

    signal.signal(signal.SIGINT, _handler)

    tw.wait()
