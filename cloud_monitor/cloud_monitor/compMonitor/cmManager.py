#!/usr/bin/python
'''
Created by LBJ
Collect message from subsystem's CompMonitor
'''

import time
import socket
import os
import json
from common.mylogger import * 
from common.configobj import ConfigObj
from common.package import Package
from common.sockcontext import PollContext, SocketContext

config_dir = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'conf' + os.sep + 'CompMonitor_example.conf'
config = ConfigObj(config_dir, encoding = 'UTF-8')

logger = getlogger('cmManager', config["LOG_PATH"] + os.sep + "cmManager.log")

def get_local_ip():
	return socket.gethostbyname(socket.gethostname())


class Manager():
	
	def __init__(self):
		self.server_ip = config['SERVER_IP']
		self.server_port = int(config['SERVER_PORT'])
		self.manager_port = int(config['MANAGER_PORT'])
		self.server_addr = (self.server_ip, self.server_port)
		self.manager_addr = ('127.0.0.1', self.manager_port)
		self.queue = {}
		self.local_ip = '127.0.0.1'
	
	def start(self):
		logger.info("Start: cmManager is running...")
		self.running = True
	
	def collect_data(self):
		logger.info("Start collect data from CompMonitor.")
		context = PollContext(self.manager_addr)
		context.initialize()
		while self.running:
			events = context.wait()
			for event, data, sock in events:
				if event == "DATA":
					logger.info("Receive data: %s" % data)
					self.put_data(data)
	
	def stop(self):
		self.running = False
		logger.info("Stop: cmManager is stopping")
	
	def wait(self):
		self.collect_data()

	def put_data(self, data):
		'''
			@params: data = {'subsys': 'aaa', 'time': 1234, 'comps':[], 'value': 3, 'host': ''}
		'''
		data = json.loads(data)
		data['nums'] = len(data['comps'])
		subsys = data['subsys']
		if self.queue.has_key(subsys):
			if self.queue[subsys]['time'] < data['time']:
				self.send_data(self.server_addr, json.dumps(self.queue[subsys]))
				self.queue[subsys] = {'time': data['time'], \
										'sysName': data['subsys'], \
										'sysMan': self.local_ip, \
										'comps': [data['host'], data['comps']], \
										'value': data['value'],
										'nums': data['nums']}
			else:
				self.queue[subsys]['comps'].append(data['host'])
				self.queue[subsys]['comps'].append(data['comps'])
				self.queue[subsys]['nums'] += data['nums']
				self.queue[subsys]['value'] = (self.queue[subsys]['value'] << data['nums']) + data['value']
				

		else:
			self.queue[subsys] = {'time': data['time'], \
									'sysName': data['subsys'], \
									'sysMan': self.local_ip, \
									'comps': [data['host'], data['comps']], \
									'value': data['value'],
									'nums': data['nums']}
		#print self.queue	
	
	def send_data(self, addr, data):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		times = 0
		package = Package("DATA", data)
		try:
			sock.connect(addr)
			sock.send(package.serialize())
			sock.close()
			logger.info("Send data to server successfully")
		except socket.error, e:
			logger.error("Cannot connect to server[%s]" % str(addr))

if __name__ == '__main__':
	man = Manager()
	man.start()
	man.wait()
