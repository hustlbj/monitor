#1/usr/bin/python
'''
Created by LBJ
'''

import os
import socket
import time
import json
import pymongo
from common.mylogger import *
from common.configobj import ConfigObj
from common.package import Package
from common.sockcontext import PollContext, SocketContext


config_dir = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'conf' + os.sep + 'CompMonitor_example.conf'
config = ConfigObj(config_dir, encoding = 'UTF-8')

logger = getlogger('CMServer', config["LOG_PATH"] + os.sep + "cmServer.log")

DB_SERVER = '127.0.0.1'
DB_PORT = 27017
DB_USER = ''
DB_PWD = ''
DB_NAME = 'comp_monitor_data'
TABLE_NAME = 'status_info'

class DBWrapper():
	
	def __init__(self, ip, port, user, pwd, db):
		self.ip = ip
		self.port = port
		self.user = user
		self.pwd = pwd
		self.db = db
	
	def connect(self):
		try:
			conn = pymongo.Connection(self.ip, self.port)
			return conn[self.db]
		except Exception, e:
			logger.error(str(e))
			return None
	
	def store(self, table, data):
		db = self.connect()
		try:
			collection = db[table]
			return collection.insert(data)
		except Exception, e:
			logger.error(str(e))
		return None
	
	def find(self, table, condition, return_col = {}):
		db = self.connect()
		try:
			collection = db[table]
			cursor = collection.find(condition, return_col)
			return [cursor.next() for i in range(0, cursor.count())]
		except Exception, e:
			logger.error(str(e))
		return None
	
	def find_by_order(self, table, condition, return_one, order_col, order = pymongo.ASCENDING):
		db = self.connect()
		try:
			collection = db[table]
			cursor = collection.find(condition).sort(order_col, order) 
			ret_list = [cursor.next() for i in range(0, cursor.count())]
			logger.debug(str(ret_list))
			if len(ret_list) > 0:
				if return_one:
					return ret_list[len(ret_list) - 1]
				else:
					return ret_list
			else:
				return None
		except Exception, e:
			logger.error(str(e))
		return None

	def update(self, table, condition, data):
		db = self.connect()
		try:
			collection = db[table]
			return collection.update(condition, {"$set": data})
		except Exception, e:
			logger.error(str(e))
		return None
	
	def store_new_status(self, table, data):
		return self.store(table, data)

	def release(self, conn):
		pass

class Server():

	def __init__(self):
		self.addr = ('127.0.0.1', int(config['SERVER_PORT']))
		self.db = DBWrapper(DB_SERVER, DB_PORT, DB_USER, DB_PWD, DB_NAME)

	def start(self):
		self.running = True
		logger.info("Start: cmServer is running...")

	def collect_data(self):
		logger.info("Start collect data from SysManager.")
		context = PollContext(self.addr)
		context.initialize()
		while self.running:
			events = context.wait()
			for event, data, sock in events:
				if event == "DATA":
					logger.debug("Receive data: %s" % data)
					self.store_data(json.loads(data))
	
	def store_data(self, data):
		record = self.db.find_by_order(data['sysName'], {}, True, 'time', pymongo.ASCENDING)
		if record and record == {'sysMan': data['sysMan'], 'comps': data['comps'], 'value': data['value'], 'nums': data['nums'], 'time': record['time'], '_id': record['_id']}:
			self.db.update(data['sysName'], {'_id': record['_id']}, {'time': data['time']})
			logger.info("Update Same status: %s" % data)
		else:
			if self.db.store(data['sysName'], {'sysMan': data['sysMan'], 'comps': data['comps'], 'nums': data['nums'], 'value': data['value'], 'time': data['time']}):
				logger.info("Store new status: %s" % data)
			else:
				logger.error("Failed to store new status: %s" % data)

	def stop(self):
		self.running = False
		logger.info("Stop: cmServer is stopping...")
	
	def wait(self):
		self.collect_data()

if __name__ == '__main__':
	svr = Server()
	svr.start()
	svr.wait()

	#db = DBWrapper(DB_SERVER, DB_PORT, DB_USER, DB_PWD, DB_NAME)
	#print db.store('test, '{'name': 'ddd'})
	#print db.find('test', {'name': 'ddd'})

