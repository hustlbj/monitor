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
from database import date_to_stamp

root_dir = path.dirname(path.abspath(__file__)) + path.sep
CONF = ConfigObj(root_dir + "scheduleserver.conf")
config_logging(CONF['log_file'])
logger = getlogger('SchedServer')


class SchedServer():

	def __init__(self):
		self.event = threading.Event()
		self.conf_db = (CONF['db']['addr'], CONF['db'].as_int('port'), \
						CONF['db']['db'], CONF['db']['meta_collection'])
		self.conf_col = (CONF['collection'].as_int('max_size'), \
						CONF['collection'].as_int('max_num'))
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
						if len(data_dict['value']) > 0:
							self.store_hosts_statistics(data_dict['from'], {'day': data_dict['day'],\
									'hosts': data_dict['value']})
							self.store_cluster_statistics(data_dict)
							logger.info("Store %s's statistics." % data_dict['from'])
						else:
							logger.info("%s's data package had noting." % data_dict['from'])
			except Exception, e:
				logger.error(str(e))


	def store_hosts_statistics(self, database, data):
		try:
			conn = pymongo.Connection(self.conf_db[0], self.conf_db[1])
			db = conn[database]
			agent_set = db.collection_names()
			try:
				agent_set.remove('system.indexes')
				agent_set.remove('metadata')
			except Exception:
				pass
			for host in data['hosts']:

				col = db['metadata']
				col.update({'name': host['name']}, {'name': host['name'], \
					'type': host['type'], 'day': date_to_stamp(data['day']), \
					'info': host['info']}, True)
				if host['type'] == 'physical':
					host['name'] = 'p_' + host['name']
				else:
					host['name'] = 'v_' + host['name']
				if host['name'] not in agent_set:
					db.create_collection(host['name'], capped=True, \
						size = self.conf_col[0] * 1000, max = self.conf_col[1])
					agent_set.append(host['name'])
				col = db[host['name']]
				col.update({'day': date_to_stamp(data['day'])}, \
				{'day': date_to_stamp(data['day']), 'value': host['value']}, True)
				
				#col.insert({'day': data['day'], 'value': host['value']})
		except Exception, e:
			logger.error(str(e))


	def store_cluster_statistics(self, data):
		p_num = 0
		v_num = 0
		p_CPU_num = 0
		p_CPU_Hz_aver = 0.0
		p_Cache_size = 0.0
		p_Mem_size = 0.0
		p_Disk_size = 0.0
		p_CPU_usage_aver = 0.0
		p_Mem_used_total = 0.0
		for value in data['value']:
			if value['type'] == 'physical':
				p_num += 1
				p_CPU_num += value['info']['cpu']['cpu_num']
				p_CPU_Hz_aver += float(value['info']['cpu']['cpu_MHz'].strip())
				p_Mem_size += value['info']['mem_total']
				p_CPU_usage_aver += value['value']['cpu_usage']['aver']
				p_Mem_used_total += value['value']['mem_used']['aver']
				for disk in value['info']['disks']:
					p_Disk_size += value['info']['disks'][disk]['size']
				try:
					cache = float(value['info']['cpu']['cache_size'][:-3].strip())
					p_Cache_size += cache
				except Exception:
					pass
			else:
				v_num += 1
		p_CPU_Hz_aver /= p_num
		p_CPU_usage_aver /= p_num
		statistics = {'cluster': data['from'], 'update_time': data['day'], \
						'p_num': p_num, 'v_num': v_num, 'p_cpu_num': p_CPU_num, \
						'p_mem_size': p_Mem_size, 'p_disk_size': p_Disk_size, \
						'p_cache_size': p_Cache_size, 'p_cpu_hz_aver': p_CPU_Hz_aver, \
						'p_cpu_usage_aver': p_CPU_usage_aver, 'p_mem_used_total': p_Mem_used_total}
		try:
			conn = pymongo.Connection(self.conf_db[0], self.conf_db[1])
			db = conn[self.conf_db[2]]
			col = db[self.conf_db[3]]
			col.update({'cluster': statistics['cluster']}, statistics, True)
		except Exception, e:
			logger.error(str(e))


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
