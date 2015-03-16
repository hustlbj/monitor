#!/usr/bin/python

'''
Created by LBJ
This script can monitor components
'''

import os
import sys
import time
import socket
import subprocess
import datetime
import json
from common.mylogger import *
from common import configobj
from common.package import Package


config_dir = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'conf' + os.sep + 'CompMonitor_example.conf'
config = configobj.ConfigObj(config_dir, encoding = 'UTF-8')
log_file = config["LOG_PATH"] + os.sep + "cmMonitor.log"

logger = getlogger("cmMonitor", log_file)

class Monitor():
	
	def __init__(self):
		self.report_message = {}
		self.retry = int(config['RETRY'])
		self.retry_interval = int(config['RETRY_INTERVAL'])
		self.port = int(config['MANAGER_PORT'])
		self.monitor_interval = int(config['MONITOR_INTERVAL'])
		self.local_ip = self.get_local_ip()
		self.first_const = 9
		self.second_const = 2
	
	def get_subsystems(self, config):
		return config.keys()[self.first_const:] if len(config.keys()) > self.first_const else []
	
	def cmd(self, command, ignore = True, timeout = -1):
		class Alarm(Exception):
			pass
		
		def alarm_handler(signum, frame):
			raise Alarm

		process = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		if timeout != -1:
			signal.signal(signal.SIGALARM, alarm_handler)
			signal.alarm(timeout)
		try:
			stdout, stderr = process.communicate()
			if timeout != -1:
				signal.alarm(0)
		except Alarm:
			pid = process.pid
			try:
				os.kill(pid, signal.SIGKILL)
			except OSError:
				pass
			return -1, 'timeout!'
		stdout = '' if ignore else stdout
		return process.returncode, stdout
	
	def cmd_prefix(self, conf):
		if conf.has_key('is_root') and int(conf['is_root']) == 1:
			return 'sudo '
		else:
			return ''
	
	def is_process_exist(self, prefix, script, timeout = -1):
		command = prefix + " ps aux | grep '%s' | grep -v grep " % script
		result = self.cmd(command, False, timeout)
		if result[0] == 0:
			ret = True if result[1] else False
			pid = int(result[1].strip().split()[1].strip()) if result[1] else -1
			return [ret, pid]
		else:
			return [False, -1]
	
	def get_local_ip(self):
		return socket.gethostbyname(socket.gethostname())

	def execute(self, config):
		sub_systems = self.get_subsystems(config)
		now = int(time.time())
		for sub in sub_systems:
			#if config[sub].has_key(local_ip):
			#	comps = config[sub][local_ip].keys()
			#	if len(comps) > 0:
			#		temp = {}
			#		temp['man_addr'] = config[sub]['manager_addr']
			#		temp['comps'] = comps
			#		temp['value'] = 0
			#		for comp in comps[1:]:
			#			temp['value'] = (temp['value'] << 1) + \
			#			int(self.is_process_exist('' ,\
			#			config[sub][local_ip][comp]['script'])[0])
			#		self.report_message[sub] = temp
			#else:
				#print config[sub]
			comps = config[sub].keys()[2:] if len(config[sub].keys()) > 2 else []
			temp = {}
			temp['man_addr'] = config[sub]['manager_addr']
			temp['comps'] = comps
			temp['value'] = 0
			for comp in comps:
				temp['value'] = (temp['value'] << 1) + \
					int(self.is_process_exist('', \
						config[sub][comp]['script'])[0])
			self.report_message[sub] = temp

		#self.report_message['time'] = now
		return self.report_message

	#when monitor starts, records the initial state 0, all values equals 0
	def start_execute(self, config):
		sub_systems = self.get_subsystems(config)
		#now = int(time.time())
		for sub in sub_systems:
			comps = config[sub].keys()[2:] if len(config[sub].keys()) > 2 else []
			temp = {}
			temp['man_addr'] = config[sub]['manager_addr']
			temp['comps'] = comps
			temp['value'] = 0
			self.report_message[sub] = temp
		#self.report_message['time'] = now
		return self.report_message

	def restart_process(self, conf):
		pass
	
	def report(self, addr, message):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		times = 0
		package = Package("DATA", message)
		while times < self.retry:
			try:
				sock.connect(addr)
				sock.send(package.serialize())
				sock.close()
				#logger.debug(message)
				break
			except socket.error, e:
				times += 1
				logger.error("Cannot connect to manager[%s], retry: %d" % (addr, times))
				time.sleep(self.retry_interval)
		return times
	
	def start(self):
		self.running = True
		logger.info("Start: cmMonitor is running...")
		now = int(time.time()) / self.monitor_interval * self.monitor_interval
		start_data = self.start_execute(config)
		#logger.debug(str(start_data))
		for sys in start_data.keys():
			ret = self.report((start_data[sys]['man_addr'], self.port), \
					json.dumps(
					{'time': now, \
					 'subsys': sys, \
					 'host': self.local_ip, \
					 'comps': start_data[sys]['comps'], \
					 'value': start_data[sys]['value']}))
			if ret == self.retry:
				self.running = False
				logger.error("Exit: Failed to connect when starting!")
				break
		time.sleep(self.monitor_interval)
	
	def stop(self):
		self.running = False
		logger.info("Stop: cmMonitor is stopping...");
	

	def wait(self):
		while self.running:
			now = int(time.time()) / self.monitor_interval * self.monitor_interval
			once_data = self.execute(config)
			#logger.debug(str(once_data))
			for sys in once_data.keys():
				#if key != "time":
				ret = self.report((once_data[sys]['man_addr'], self.port), \
					json.dumps(
					{'time': now, \
					 'subsys': sys, \
					 'host': self.local_ip, \
					 'comps': once_data[sys]['comps'], \
					 'value': once_data[sys]['value']}))
				if ret == self.retry:
					#self.running = False
					logger.error("Exit: Failed to connect!")
					break
			time.sleep(self.monitor_interval)
		

if __name__ == '__main__':
	mon = Monitor()
	mon.start()
	mon.wait()
