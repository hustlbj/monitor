#!/usr/bin/env python
import threading
import time
import sys
import errno
import os
import socket
import os.path as path

from include.configobj import ConfigObj
from common.sockcontext import PollContext
from common.package import Package
from common.logger import config_logging, getlogger

# Load configuration
root_dir = path.dirname(path.abspath(__file__)) + path.sep
CONF = ConfigObj(root_dir+"server.conf")
config_logging(CONF['log_file'])

from database import MongoDB


logger = getlogger("Server")

class MonServer():
	"""
	MonServer
	Contained two components, collector and register center. Each one is a thread.
	
	Collector
	1)maintain connections from workers, 2)and send DATA event to worker.3) Recieve data 4)and insert it into database

	Register center
	1)recieve request from agent 2)and return an available address of worker back
	"""

	def __init__(self):
		self.event = threading.Event()

		conf_db = CONF['db']
		self.db = MongoDB((conf_db['addr'], conf_db.as_int('port')), 
				  conf_db['db'], 
				  conf_db['meta_collection'],
				  conf_db.as_int('max_data'))
		self.collect_interval = CONF['collector'].as_int('c_interval')
		self.tasks = []

		# Set of available workers
		self.worker_set = {}


	@property	
	def running(self):
		"""
		Running or not

		:return: True if running, False otherwise
		"""
		return not self.event.isSet()


	def collector(self):
		"""
		Collector component.

		Handle each one of connections from workers by using poll.
		"""

		logger = getlogger("Collector")
		logger.info("Starting collector.")

		# Set up new poll context and initialize it
		logger.info("Setting up poll context")
		conf = CONF['collector']
		context = PollContext((conf['c_addr'], conf.as_int('c_port')))
		context.initialize()

		steps = self.collect_interval

		# Main loop
		logger.info("Collector is running")
		while self.running:

			# Wait for next event
			try:
				events = context.wait(1000)
			except Exception, e:
				logger.error(str(e))

			for event, data, sock in events:

				# No register event coming
				if event == "TIMEOUT":
					if steps > 0:
						steps -= 1
					else:
						logger.debug("Send DATA event to each one of workers")
						for key, worker in self.worker_set.items():
							# send DATA to each worker
							try:
								worker['fd'].send("DATA")
								logger.debug("send to %s"%key)

							# remove disconnected worker from worker set
							except Exception, e:
								if e.errno == errno.EBADF:
									del self.worker_set[key]
									logger.info("The connection to worker %s is closed." % key)

						steps = self.collect_interval

					break

				# New worker coming
				if event == "REGISTER":
					ip = sock.getpeername()[0]

					# initialize coming worker
					self.worker_set[ip] = {
						'fd': sock, 
						'addr': eval(data),
						'agents': 0}

					logger.info("Worker %s has registered, address on %s" % (ip, data))
					continue

				# Metric data coming
				if event == "DATA":

					# insert data into database
					count = self.db.insert_metric(data)
					logger.info("store metrics : %d" % count)

		logger.info(threading.currentThread().getName() + " is closing")


	def worker_dispatch(self):
		"""
		Assigned a worker from worker set by using different strategies.

		Strategy:	
		(Now) minimum agents, return the one handled least agents.
		same region, return the one which be in then same region with coming agent. 
		

		:returns: worker object
		"""

		# return worker whose amount of assigned agents is minimum
		target = None
		if len(self.worker_set) == 0:
			raise Exception("No avaible worker.")
		
		return min(self.worker_set.values(), key=lambda x:x['agents'])



	def registercenter(self):
		"""
		Register center component.

		Handle each one of connections from agents by using poll.
		"""

		logger = getlogger("Register")
		logger.info("Starting register center.")

		# Set up new poll context and initialize it
		conf = CONF['register']
		context = PollContext((conf['r_addr'], conf.as_int('r_port')))
		context.initialize()


		# Main loop
		logger.info("Register is running")
		while self.running:

			# Wait for arrival event
			try:
				results = context.wait(1000)
			except Exception, e:
				logger.error(str(e))

			for event, data, sock in results:
				if event == "TIMEOUT":
					break

				# New agent coming
				elif event == "REGISTER":

					# Fix name of agent
					ip = sock.getpeername()[0]
					data = eval(data)
					name = data.get('name', '') == '' and ip or data.get('name')


					# Get an available worker 
					try:
						target_worker = self.worker_dispatch()
					except Exception, e:
						logger.exception(str(e))
						sock.send('None')
						continue
					
					# Insert platform information of agent into database
					try:
						self.db.insert_host(name, data)
					except Exception ,e:
						logger.error(str(e))

					# Return worker address 
					worker_addr = target_worker['addr']
					target_worker['agents'] += 1

					sock.send(str(worker_addr))

					logger.info("New agent has registered and send data to worker %s:%s" % worker_addr)
					logger.debug("agent %s has registered."%name)


		logger.info(threading.currentThread().getName() + " is closing")


	def start(self):
		"""
		Start server.
		"""

		logger.info("Starting Mon-Server : pid %d" % os.getpid())

		self.event.clear()
		collector = threading.Thread(name='collector', target=self.collector)
		register_center = threading.Thread(name='register_center', target=self.registercenter)
		
		collector.start()
		register_center.start()

		self.tasks.append(collector)
		self.tasks.append(register_center)


	def stop(self):
		"""
		Stop server.
		"""

		self.event.set()
		logger.info("Closing server.")
		


	def wait(self):
		"""
		Wait for server's stopping.
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

		logger.info("Mon-Server is closed.")



if __name__=="__main__":

	###################### 
	#    local test		 #
	######################
	import signal

	monserver = MonServer()
	monserver.start()

	def handle_signal(signo, frame):
		print "interrupt recieved"
		monserver.stop()

	signal.signal(signal.SIGINT, handle_signal)
	signal.signal(signal.SIGTERM, handle_signal)

	monserver.wait()

