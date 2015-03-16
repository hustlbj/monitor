#!/usr/bin/env python
import time
import os
#import sys
import socket
#import errno
from database import MongoDB
import json

from include.configobj import ConfigObj
from common.package import Package
from common.logger import config_logging, getlogger
#from utils.load_config import load_metric_list

# Load configuration
root_dir = os.path.dirname(os.path.abspath(__file__)) + os.path.sep
CONF = ConfigObj(root_dir+"server.conf")
config_logging(CONF['schedule_log'])

logger = getlogger("Schedule")
MAX_HASH_CODE = 50


def hashCode33(s):
	c = str(s).encode("Latin1")
	h = 0
	for i in c:
		h = h * 33 + ord(i)
		h = h % MAX_HASH_CODE
	return h


class Schedule():


	def __init__(self):
		self.db = MongoDB((CONF['db']['addr'], CONF['db'].as_int('port')), 
				CONF['db']['db'],
				CONF['db']['meta_collection'],
				CONF['db'].as_int('max_data'))
		self.server = (CONF['schedule_server']['s_addr'], CONF['schedule_server'].as_int('s_port'))
		self.tmp = CONF['schedule_file']
		self.data_list = []
		self.metrics_value = []
		self.today = time.strftime('%Y-%m-%d', time.localtime(time.time() - 24 * 60 * 60))
		logger.info('schedule is running.')


	def collect(self, start, end, step = 30):
		physics = self.db.get_hosts()
		vms = self.db.get_hosts('virtual')
		#agent_set = self.db.agent_set
		for agent in physics:
			collection = MongoDB((CONF['db']['addr'], CONF['db'].as_int('port')),
						CONF['db']['db'], 
						agent)
			metrics_name = collection.get_metrics_name()
			value = collection.get_metrics_value(agent, metrics_name, (start, end), step)
			if len(value) > 0:
				self.metrics_value.append({'name': agent, 'value': value, 'type': 'physical'})
		for agent in vms:
			collection = MongoDB((CONF['db']['addr'], CONF['db'].as_int('port')),
						CONF['db']['db'], 
						agent)
			metrics_name = collection.get_metrics_name()
			value = collection.get_metrics_value(agent, metrics_name, (start, end), step)
			if len(value) > 0:
				self.metrics_value.append({'name': agent, 'value': value, 'type': 'virtual'})
		logger.info('collecting metrics value completed.')


	def send(self):
		grid_name = CONF['grid_name']
		retry_interval = CONF['schedule_connection'].as_int('retry_interval')
		retry_times = CONF['schedule_connection'].as_int('retry_times')
		time.sleep(hashCode33(grid_name))
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		i = 0
		flag = False
		#{'from': 'hust', 'day': '2013-10-11', 'value': [{'host1': value, 'type': physical}, {...}, {...}]}
		value = {'from': grid_name, 'day': self.today, 'value': self.metrics_value}
		package = Package('SCHE', json.dumps(value))
		while((not flag) and (i < retry_times)): 
			try:
				sock.connect(self.server)
				sock.send(package.serialize())
				sock.close()
				flag = True
				logger.info('send data to schedule server successfully.')
			except socket.error, e:
				logger.error('cannot connect to server!')
				time.sleep(retry_interval)
			i += 1
		if (not flag):
			self.__write_tmp()


	def __write_tmp(self):
		f = open(self.tmp, 'a')
		for line in self.metrics_value:
			f.write(str(line))
		f.close()


	def get_params(self):
		return (self.db, self.server, self.tmp, self.data_list, self.metrics_value)



if __name__ == "__main__":
	schedule = Schedule()
	today_start = schedule.today + ' 00:00:00'
	today_end = schedule.today + ' 23:59:59'
	schedule.collect(today_start, today_end)
	print schedule.metrics_value
	schedule.send()

