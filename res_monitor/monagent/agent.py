#!/usr/bin/env python
import os
import threading
import socket
import time
import os.path as path

from common.package import Package
from common.logger import config_logging, getlogger
from utils.load_config import load_metric_list
from utils.platform_info import get_platform_info
from utils.platform_info import get_uuid
from utils.platform_info import get_local_ip
from utils.configobj import ConfigObj

# Root directory
root_dir = path.dirname(path.abspath(__file__)) + path.sep

# Configure Object
CONF = ConfigObj(root_dir+"agent.conf")

# Configure logging
config_logging(CONF['log_file'])
logger = getlogger("Agent")


def import_module(module_name):
	temp = __import__("modules." + CONF["platform"], globals(), locals(), [module_name,])
	return getattr(temp, module_name)


class Collector(object):
    """
    Responsable for collecting metric data.
    Each one of devices assigned a collector.

    CPUModule, MemModule, LoadModule: single collector
    DiskModule, NetModule: multiple collector
    """

    def __init__(self, mod_name, metric_group, period, *args, **kwargs):
        self.mod_name = mod_name
        mod = import_module(mod_name)
        instance = getattr(mod, mod_name)(*args, **kwargs)
        self.worker = instance
        self.handler = instance.metric_handler
        self.update = instance.update

        self.metrics = []
        self.setmetricgroup(metric_group)
        self.period = period

        self.last_collect = 0
        self.device = instance.get_device()
    
    	logger.info("Initialize collector %s %s" % (mod_name, self.device and 'with divece %s'%self.device or ''))

 
    def setmetricgroup(self, metrics):
        for metric in metrics:
            if metric["enabled"] == 1:
                self.metrics.append(metric)

    def do_collect(self):

        self.update()
        
        ret = {}
        metric_prefix = self.device and  self.device+'-' or ''
        for metric in self.metrics:
            name = metric["name"]
            ret[metric_prefix+name] =self.handler(name)

        return ret



class MonAgent(object):
	"""
	docstring for MonAgent
	"""
	
	def __init__(self):
		super(MonAgent, self).__init__()

		# Mon-Server address for registering
		addr = CONF['server_addr'].split(':')
		self.server_addr = (CONF['server_addr'], CONF.as_int('server_port'))

		# Load metric list
		self.metrics = load_metric_list()["metric_groups"]

		# Set type and hostname of agent
		self.type = {True:'virtual', 
			     False: 'physical'}[CONF.as_bool('is_virtual')]
		#self.hostname = CONF.as_bool('is_virtual') and CONF.get('hostname', '') or socket.gethostname()
		self.ip = get_local_ip()
		
		if not CONF['hostname']:
			self.hostname = self.type[0] + '-' + get_uuid() + '-' + self.ip + '-' + CONF['cluster']
		else:
			self.hostname = self.type[0] + '-' + CONF['hostname'] + '-' + self.ip + '-' + CONF['cluster']
			

		# set interval time between collecting and retry
		self.collect_interval = CONF.as_int('collect_interval')
		self.retry_interval = CONF.as_int('retry_interval')
	
		self.running = False
	

	def register(self):
		"""
		Register to server and recieve address of Mon-Worker.

		:returns: address of mon-worker, type of list or tuple
		"""

		# Get platform information and fix it.
		platform = get_platform_info()
		platform['metric_groups'] = self.metrics
		platform['type'] = self.type
		platform['name'] = self.hostname
		logger.debug("platform info: %s" % platform)

		# Keep trying to register 
		# until agent is closing or recieve available worker address
		while self.running:

			server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			# keep connecting server socket
			while self.running:
				try:
					server.connect(self.server_addr)
				except socket.error, e:
					logger.error("cannot connect to server.")
					time.sleep(self.retry_interval)
				else:
					break

			# send register package with platform information
			packet = Package("REGISTER", str(platform))
			server.send(packet.serialize())

			# recieve message
			msg = server.recv(1024)
			server.close()

			# break if worker address is list or tuple,
			# sleep and next loop otherwise
			worker_addr = msg and eval(msg) or None
			if type(worker_addr) in (list, tuple):
				break	

			logger.error("Worker address is unavailable.")
			time.sleep(self.retry_interval)
				
		logger.info("Register success, worker addr: %s:%s" % worker_addr)

		return worker_addr


	def load_collectors(self):
		"""
		Load collectors.
		"""

		self.collectors = []

		for metric_group in self.metrics:
			mod_name = metric_group['name']
			if metric_group.has_key('instances'):
				for instance in metric_group['instances']:
					# create a collector WITH DIVICE
					collector = Collector(mod_name, 
            						  metric_group['metrics'], 
            						  metric_group['period'], 
            						  **instance)

					self.collectors.append(collector)
			else:
				# create a collector WITHOUT DEVICE
				collector = Collector(mod_name, 
						metric_group['metrics'], 
						metric_group['period'])

				self.collectors.append(collector)
		

	def start(self):
		"""
		Start agent.
		"""

		logger.info("Starting Agent")

		# Set running flag
		logger.info("Agent is running")
		self.running = True

		# Register to server and recieve worker address
		self.worker_addr = self.register()

		# Load collectors
		self.load_collectors()


	def stop(self):
		"""
		Stop agent.
		"""
		self.running = False

	def wait(self):
		"""
		Main loop of agent.
		"""

		while self.running:
			
			# collect metric information 
			retval = {}
			for collector in self.collectors:
			    ret = collector.do_collect()
			    retval.update(ret)

			# format metric data and package it
			data = [self.hostname, [time.time(), retval]]
			logger.debug("time: %s, data: %s" % (str(data[1][0]), str(data[1][1]) ))

			packet = Package("DATA", str(data)) 

			
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			# connect to worker and send data
			try:
				sock.connect(self.worker_addr)
				sock.send(packet.serialize())
				sock.close()

			# re-register to server and ask for new worker address if error occur
			except socket.error, e:
				logger.info("Worker is unavailable, now re-register to server.")
				self.worker_addr = self.register()

			# sleep until next collecting
			time.sleep(self.collect_interval)


		logger.info("Mon-Agent is closed")


if __name__ == "__main__":

	monagent = MonAgent()
	monagent.start()
	import signal
	def handle_signal(signo, frame):
		print "interrupt recieved"
		monagent.stop()
	signal.signal(signal.SIGINT, handle_signal)
	signal.signal(signal.SIGTERM, handle_signal)

	monagent.wait()

    
   
