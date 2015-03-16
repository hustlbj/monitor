#!/usr/bin/python
'''
Created by LBJ
Collect message from subsystem's CompMonitor
'''

import pymongo
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

logger = getlogger("CompMonAPI", config["LOG_PATH"] + os.sep + "cmMonAPI.log")

DB_SERVER = '127.0.0.1'
DB_PORT = 27017
DB_USER = ''
DB_PWD = ''
DB_NAME = 'comp_monitor_data'

class CompMonAPI:

	def __init__(self):
		self.comps = self.getAllCompsName()

	def connect(self):
		try:
			conn = pymongo.Connection(DB_SERVER, DB_PORT)
			return conn[DB_NAME]
		except Exception, e:
			logger.error(str(e))
			return None

	def getAllCompsName(self):
		db = self.connect()
		comps = db.collection_names()
		try:
			comps.remove('system.indexes')
		except Exception, e:
			pass
		return comps

	def getAllStat(self):
		db = self.connect()
		collections = self.comps
		all_stat = {}
		try:
			if collections:
				for subsys in collections:
					collection = db[subsys]
					stats = collection.find({}, {'_id': 0}).sort('time', pymongo.DESCENDING)
					if stats and stats.count() > 0:
						all_stat[subsys] = stats.next()
						all_stat[subsys]['time'] = self.stampToDate(all_stat[subsys]['time'])
		except Exception, e:
			logger.error(str(e))
		return all_stat

	def getOneStat(self, groupName):
		db = self.connect()
		try:
			collection = db[groupName]
			stat = collection.find({}, {'_id': 0}).sort('time', pymongo.DESCENDING)
			if stat and stat.count() > 0:
				one = stat.next()
				one['time'] = self.stampToDate(one['time'])
				return one
		except Exception, e:
			logger.error(str(e))
		return {}

	def dateToStamp(self, oneDate):
		try:
			timeArray = time.strptime(oneDate, "%Y-%m-%d %H:%M:%S")
			timeStamp = int(time.mktime(timeArray))
			return timeStamp
		except Exception, e:
			logger.error(str(e))
			return None

	def stampToDate(self, oneStamp):
		return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(oneStamp))


	def getGroupFSM(self, groupName, startTime, endTime):
		startTime = self.dateToStamp(startTime)
		endTime = self.dateToStamp(endTime)
		if startTime == None:
			startTime = 0
		if endTime == None:
			endTime = int(time.time())
		FSM = []
		if endTime < startTime:
			return FSM
		db = self.connect()
		try:
			collection = db[groupName]
			stats = collection.find({'time': {'$lte': endTime}, 'time': {'$gte': startTime}}, {'_id': 0}).sort('time', pymongo.ASCENDING)
			if stats and stats.count() > 0:
				for i in range(0, stats.count()):
					stat = stats.next()
					FSM.append(self.stampToDate(stat['time']))
					FSM.append(stat['comps'])
					FSM.append(stat['nums'])
					FSM.append(stat['value'])
		except Exception, e:
			logger.error(str(e))
		return FSM


