#!/usr/bin/env python
import time
import threading
import Queue
import random
import socket
import os
import sys
import os.path as path

from include.configobj import ConfigObj
from common.package import Package
from common.sockcontext import PollContext, SocketContext
from common.logger import config_logging, getlogger

root_dir = path.dirname(path.abspath(__file__)) + path.sep

# Load config file
CONF = ConfigObj(root_dir+"worker.conf")
config_logging(CONF['log_file'])

from pool import MetricPool

logger = getlogger("Worker")


class MonWorker():
	"""
	MonWorker
	Contained two components, collector and frontier. Each one is thread.
	
	Collector
	1)recieve metric data from agent, and 2)put fixed data into queue which is thread-safe.

	Frontier
	1)recieve DATA event from main socket. If socket timeout, 2)pop data from queue and 3)insert it into metric pool.
	"""

	def __init__(self):
		self.event = threading.Event()
		self.retry_interval = CONF.as_int('retry_interval')
		self.tasks = []
		self.data_queue = Queue.Queue(CONF.as_int('queue_max'))
		self.pool = MetricPool()

		self.collector_addr = (CONF['collector']['c_addr'], CONF['collector'].as_int('c_port'))


	@property
	def running(self):
		"""
		Running or not.
		"""
		return not self.event.isSet()


	def collect_data(self):
		"""
		Collector component
		"""

		logger = getlogger("Collector")
		logger.info("Starting collector.")

		# Set up poll context and initialize it
		logger.info("Setting up poll context")
		context = PollContext(self.collector_addr)
		context.initialize()

		# Main loop
		while self.running:

			# Wait for next events
			try:
				events = context.wait(1000)
			except Exception, e:
				logger.error(str(e))
				continue

			for event, data, sock in events:
				if event == "TIMEOUT":
					break

				# put data into data queue
				data = eval(data) 
				try:
					entry = (
						data[0] != '' and data[0] or sock.getpeername()[0],
						data[1]
					)
				except Exception, e:
					logger.error(str(e))
					continue 

				logger.debug(str(entry))
				self.data_queue.put(entry)
				logger.debug("recieve message from %s" % entry[0])

		logger.info("%s is closing" % threading.currentThread().getName())


	def process_request(self, context):
		"""
		Frontier component

		Handle DATA event from server, and deal data
		"""

		logger = getlogger("Frontier")
		logger.info("Starting frontier.")		

		# Main loop
		while self.running:

			event = context.wait()

			# Handle DATA event
			if event == "DATA":
				logger.debug("Recieve DATA.")

				packet = Package("DATA", self.pool.dump())
				context.send(packet.serialize())

			# Handle data from queue
			# handle with 100 data at most in each time slice
			elif event == "TIMEOUT":
				for i in range(100):
					try:
			 			entry = self.data_queue.get_nowait()
						self.pool.insert(*entry)
			 		except Queue.Empty, e:
			 			break
			 		except Exception, e:
						logger.error(str(e))
						break

				if i:
				    logger.debug("Processing data: %d" % (i+1))

		 		continue

			# If socket broken, re-register to server
			elif event == '':
				context = self.register(context)

		logger.info("%s is closing" % threading.currentThread().getName())


	def register(self, context):
		"""
		Register to server.

		:param context: socket context related to server end
		:returns: new socket context after register successfully
		"""

		while self.running:

			# Connect to server and send REGISTER package
			try:
				context.initialize()
				context.settimeout(None)
        		        context.send(
                      			Package("REGISTER", str(self.collector_addr)).serialize()
                		)
				break
			except socket.error, e:
				logger.error("cannot connect to server: %s", str(e))
			except Exception, e:
				logger.error(str(e))

			time.sleep(self.retry_interval)
		
                logger.info("Registered from Mon-Server...")
		
                context.settimeout(1.0)

		return context
	

	def start(self):
		"""
		Start worker.
		"""

		logger.info("Worker is starting...")

		# Initialize socket context related to server
		# and register to server
		worker_context = SocketContext((CONF['server']['s_addr'], CONF['server'].as_int('s_port')))
		worker_context = self.register(worker_context)	
		

		# Start components
		frontier = threading.Thread(name="frontier", 
					    target=self.process_request, 
					    args=(worker_context,))
		collector = threading.Thread(name="collector", 
					     target=self.collect_data)

		frontier.start()
		collector.start()

		self.tasks.append(frontier)
		self.tasks.append(collector)


	def stop(self):
		"""
		Stop worker.
		"""

		self.event.set()
		logger.info("Closing worker...")


	def wait(self):
		"""
		Wait for worker exiting.
		"""
                while self.running:
                        time.sleep(30)
                        isdown = False
                        for task in self.tasks:
                                if not task.isAlive() and self.running:
                                        isdown = True
                        if isdown:
                                self.stop()
                                time.sleep(5)
                                self.start()

                # Wait each one of threads quiting
                for task in self.tasks:
                        if task.isAlive():
                                task.join()

		logger.info("Mon-Worker is closed")


if __name__ == "__main__":

	import sys
	import os.path as path

	curdir = path.dirname(path.abspath(__file__))
	pardir = path.dirname(curdir)
	sys.path.append(pardir)
	
	import signal

	monworker = MonWorker()
	monworker.start()

	def handle_signal(signo, frame):
		print "interrupt recieved"
		monworker.stop()

	signal.signal(signal.SIGINT, handle_signal)

	monworker.wait()
	


