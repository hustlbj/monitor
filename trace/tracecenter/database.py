#!/usr/bin/env python

import pymongo
import time

from common.logger import config_logging, getlogger
config_logging('/tmp/tracecenter.log')
logger = getlogger("MongoDB")


class MongoDB(object):
	"""
	Handle database operation with MongoDB
	"""

	def __init__(self, hostaddr, dbname):
		super(MongoDB, self).__init__()
		self.hostaddr = hostaddr
		self.dbname = dbname


	def clearall(self):
		"""
		Clear all information in database.
		Emplty database.
		"""

		conn = pymongo.Connection(*self.hostaddr)
		conn.drop_database(self.dbname)


	def insert_traces(self, entrylist):

		count = 0
		conn = pymongo.Connection(*self.hostaddr)
		db = conn[self.dbname]
		for api, data in entrylist.items():
			collection = db[api]
			stat = {'normal':0, 'timeout':0, 'failed':0}
			for entry in data:
				try:
					collection.insert(entry)
					stat[entry['category']] += 1
				except Exception, e:
					logger.error(str(e))
				else:
					count += 1
			collection.update({'flag':'statistics'}, {'$inc':stat}, True)
		return count

	# modified by LBJ
	def set_traces_abnormal(self, path, traces):
		logger.warn('database.set_traces_abnormal: %s, %d', path, len(traces))
		if len(traces) > 0:
			conn = pymongo.Connection(*self.hostaddr)
			db = conn[self.dbname]
			collection = db[path]
			for trace in traces:
				try:
					collection.update({'id': trace['id']}, {'$set':{'category': 'timeout'}});
				except Exception, e:
					logger.error(str(e))
			try:
				collection.update({'flag': 'statistics'}, {'$set': {'timeout': len(traces)}})
			except Exception, e:
				logger.error(str(e))

	def get_paths(self):
		"""
		"""

		connection = pymongo.Connection(*self.hostaddr)
		db = connection[self.dbname]
		collections = db.collection_names()
		collections.remove('system.indexes')
		#print 'database.get_paths: collections', collections
		if 'report' in collections:
			collections.remove('report')
		
		ret = []
		for path in collections:
			data = {}
			# modified by LBJ...........2015/6/30
			# print 'database.get_paths: path', path
			paths = path.split('-')
			data['pack'] = paths[0]
			data['cls'], data['func'] = paths[1].split('.')
			#print 'database.get_paths: data', data
			rlt = db[path].find_one({'flag':'statistics'}, {'_id': 0, 'flag': 0})
			data.update(rlt)

			last_entry = db[path].find().sort("time", pymongo.DESCENDING).limit(1)
			if last_entry.count():
				data['lasttime'] = time.strftime("%c", time.localtime(last_entry[0]['time']))
			else:
				data['lasttime'] = 'wait first'
			ret.append(data)
			#print ret

		return ret




	def get_traces(self, interface, time_section=None):
		"""
		"""

		connection = pymongo.Connection(*self.hostaddr)
		db = connection[self.dbname]
		collection = db[interface]

		# Get last docment in specified collection.
		def getlast():
			return collection.find().sort("time", pymongo.DESCENDING).limit(1)

		last_entry = getlast()
                if not last_entry.count():
			return []

		if not time_section:
			return list(last_entry)

                last_entry = last_entry[0]
		# If start time of time section is negitive, get data from tail of collection.
		if time_section[0] < 0:
			time_filter = {'$gt': int(last_entry['time'])+time_section[0]}

		# Otherwise get data normally.
		else:
			time_filter = {'$gt': time_section[0], '$lt': time_section[1]} 
		

		# Read data from database
		ret = collection.find({'time':time_filter}, {'_id': 0})
		return list(ret)


	def insert_report(self, report):
		"""
		"""

		connection = pymongo.Connection(*self.hostaddr)
		db = connection[self.dbname]
		collection = db['report']

		collection.update({'path':report['path'], 'func':report['func'], 'from':report['from'], 'to':report['to']}, report, True)
		
	def get_report(self, path, func):
		"""
		"""

		connection = pymongo.Connection(*self.hostaddr)
		db = connection[self.dbname]
		collection = db['report']

		report = collection.find({"path": path, "func":func}, {'_id':0}).sort("to", pymongo.DESCENDING).limit(1)
		if not report.count():
			return []

		return report[0]

	def get_path_report(self, path):
		"""
		"""

		connection = pymongo.Connection(*self.hostaddr)
		db = connection[self.dbname]
		collection = db['report']

		last = collection.find({"path": path}, {'_id':0}).sort("to", pymongo.DESCENDING).limit(1)
		if not last.count():
			return []

		report = collection.find({"path": path, "to": last[0]['to']}, {'_id':0})

		ret = {}
		for item in sorted(report, key=lambda x:x['to']):
			ret[item['func']] = item

		rlt = []
		for item in ret.values():
			entry = {"func": item["func"], 
                                 "total": item["total"], 
                                 "anomaly": item["total"]-item["normal"]['size']}
			rlt.append(entry)

		return rlt



if __name__=="__main__":
	import pprint
	db = MongoDB(("202.114.10.146", 27017), "newtrace")
	#print db.get_trace('IaaSAPI-IaaSAPI.get_hostpool_info')
	#print db.get_report('IaaSAPI-IaaSAPI.get_vmpool_info', 'IaaSOperation-IaaSOperation.get_vmpool_info')
	pprint.pprint( db.get_path_report('IaaSAPI-IaaSAPI.get_vmpool_info'))
	#print db.get_trace('IaaSAPIaSAPI.get_hostpool_info', (-500, None))
	#print db.get_paths()
	#db.clearall()
