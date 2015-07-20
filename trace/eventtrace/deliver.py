#!/usr/bin/env python

import socket
import time
import os
import threading
import Queue

from injection import SOCKFILE
from common.logger import config_logging, getlogger
from common.package import Package

config_logging('/tmp/tragentd.log')

logger = getlogger('Deliver')

class TraceDeliver(object):
    
    def __init__(self):
        self.sock_addr = SOCKFILE
        self.queue = Queue.Queue()
        self.tasks = []
        self.event = threading.Event()

        self.report_max = 500
        self.report_interval = 5
        self.server_addr = ("202.114.10.146", 41065)

    @property
    def running(self):
        """
        Running or not.
        """
        return not self.event.isSet()

    def start(self):
        collector_thread = threading.Thread(target=self.collector, name="Collector")
        reporter_thread = threading.Thread(target=self.reporter, name="Reporter")
        
        collector_thread.start()
        reporter_thread.start()
        
        self.tasks.append(collector_thread)
        self.tasks.append(reporter_thread)

    def collector(self):
        logger.info("Collector is starting...")
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.settimeout(1.0)
        sock.bind(self.sock_addr)
        os.system("sudo chown crane:crane %s" % SOCKFILE )

        while self.running:
            try:
                msg, addr = sock.recvfrom(4096)
                entry = eval(msg)
                logger.debug(str(entry))
     
                self.queue.put(entry)
            except socket.timeout, e:
                pass
            
        sock.close()
        logger.info("Collector is closing...")


    def reporter(self):
        logger.info("Reporter is starting...")

        while self.running:
            report = []
            while self.running:
                try:
                    entry = self.queue.get_nowait()
                    report.append(entry)
                    if len(report) > self.report_max:
                        break
                except Queue.Empty, e:
                    break
                 
            try:            
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(self.server_addr)
                packet = Package('DATA', str(report))
                sock.send(packet.serialize())
                sock.close()
                logger.debug("Trace log send: %d" % len(report))
            except socket.error, e:
                logger.error(str(e))
                time.sleep(5)

            if self.queue.empty():
                for i in range(self.report_interval):
                    time.sleep(1)
                    if not self.running:
                        break


        logger.info("Reporter is closing...")


    def stop(self):
        self.event.set()


    def wait(self):
        while self.running:
            time.sleep(1)

        for task in self.tasks:
            if task.isAlive():
                task.join()
        os.remove(self.sock_addr)


if __name__=="__main__":
    import signal

    td = TraceDeliver()
    td.start()
    
    def _handler(a,b):
        print 'close'
        td.stop()

    signal.signal(signal.SIGINT, _handler)
    td.wait()
