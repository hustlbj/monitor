#!/usr/bin/env python

import pymongo
import time
import re

from common.logger import getlogger

logger = getlogger("MongoDB")


class MongoDB(object):
	"""
	Handle database operation with MongoDB
	"""

	def __init__(self, hostaddr, dbname, metadata, coll_max=86400):
		super(MongoDB, self).__init__()
		self.hostaddr = hostaddr
		self.dbname = dbname
		self.metadata = metadata
		self.collection_max = coll_max 
		self.agent_set = []

		# Get names of agents stored in database already
		conn = pymongo.Connection(*self.hostaddr)
		dbnames = conn.database_names()
		if self.dbname in dbnames:
			self.agent_set = conn[self.dbname].collection_names()
			try:
				self.agent_set.remove('system.indexes')
				self.agent_set.remove(self.metadata)
			except:
				pass
		

	def clearall(self):
		"""
		Clear all information in database.
		Emplty database.
		"""

		conn = pymongo.Connection(*self.hostaddr)
		conn.drop_database(self.dbname)


	def insert_metric(self, entrylist):
		"""
		Insert metric data into database

		:param entrylist: metric infomation of different agent.
			{'123':[[time, val], ..., [time, val]], 
					...
			 '234':[[time, val], ..., [time, val]]}
		:returns: count of total insertion.
		"""

		if type(entrylist) is str:
			entrylist = eval(entrylist)
		count = 0
		conn = pymongo.Connection(*self.hostaddr)
		db = conn[self.dbname]
		for host, data in entrylist.items():
			collection = db[host]
			for entry in data:
				try:
					collection.insert({'time':entry[0], 'metrics':entry[1]})
					#update the latest timestamp
					metadata = db[self.metadata]
					logger.debug(host + ": " + str(entry[0]))
					metadata.update({'name': host}, {'$set': {'time': int(entry[0])}}, True)
				except Exception, e:
					logger.error(str(e))
				else:
					count += 1
		return count

	def insert_host(self, host, info):
		"""
		Insert platform information of agents.

		:param host: name of agent.
		:param info: information of agent.
		"""

		if type(info) is str:
			info = eval(info)	

		# Fix common host info
		fixed_info = {}
		fixed_info['id'] = host

		info.pop('virt_type', None)
		components = info.pop('components')
		fixed_info['cpu'] = components['cpu']
		fixed_info['mem_total'] = components['memory']['mem_total']

		if components.has_key('network'):
			fixed_info['network_interfaces'] = components['network']
			fixed_info['network_interfaces'].pop('lo', None)

		# Fix disk info as:
		# disks:
		#	sda:
		#		size:
		#		partitions:
		#			sda2: 
		#			sda1:
		if not components['filesystem'].has_key('local'):
			components['filesystem']['local'] = {}

		disks = {}
		for diskkey, diskval in sorted(components['filesystem']['local'].items()):
			if not diskval.has_key('disk'):
				disks[diskkey] = diskval
				disks[diskkey]['partitions'] = {}
			else:
				disks[diskval['disk']]['partitions'][diskkey] = diskval
		for diskkey, diskval in disks.items():
			if not len(diskval['partitions']):
				disks.pop(diskkey)
		fixed_info['disks'] = disks

		# Fix metrics
		fixed_metrics = {}
		for group in info.pop('metric_groups'):
			fixed_metrics[group['name']] = group['metrics']

		fixed_info['os'] = components['os']
		info['info'] = fixed_info
		info['metrics'] = fixed_metrics

		# Insert host information into database
		conn = pymongo.Connection(*self.hostaddr)
		db = conn[self.dbname]
		metadata = db[self.metadata]

		info['name'] = host
		info['flag'] = 'host'
		info['time'] = int(time.time())
		metadata.update({'name': host, 'flag': 'host'}, info, True)

		# If host is new registered, create a new capped collection.
		# set size of single document as 1000 bytes
		# and set max amount of documents
		if host not in self.agent_set:
			db.create_collection(host, capped=True, size=self.collection_max*1000, max=self.collection_max)
			self.agent_set.append(host)


	def get_host(self, host, key_filter=None):
		"""
		Get host information from metadata collection.

		:param host: name of agent
		:param key_filter: filter of result, default None, dict
		:returns: host information object, dict
		"""

		connection = pymongo.Connection(*self.hostaddr)
		db = connection[self.dbname]
		metadata = db[self.metadata]

		if key_filter:
			key_filter = {key_filter: 1}

		ret = metadata.find_one({'flag':'host', 'name': host}, key_filter)		
		return ret


	def get_metric(self, host, metric, time_section=None, step=30):
		"""
		Get metric data.

		:param host: name of agent, str
		:param metric: name of metric, str
		:param time_section: start and end time to read, tuple
		:param step: time step between return data, int
		:returns: metric data, list.
		          each element is list, first of it is time, second of it is real data.  
		"""

		connection = pymongo.Connection(*self.hostaddr)
		db = connection[self.dbname]
		host_coll = db[host]

		# Get last docment in specified collection.
		def getlast():
			return host_coll.find({}, {'time': 1}).sort("time", pymongo.DESCENDING).limit(1)

		last_entry = getlast()
		if not last_entry.count():
			return []
		last_entry = last_entry[0]

		if not time_section:
			time_section = (-step, None)

		# If start time of time section is negitive, get data from tail of collection.
		if time_section[0] < 0:
			time_filter = {'$gt': int(last_entry['time']/step)*step + time_section[0] + step}

		# Otherwise get data normally.
		else:
			time_filter = {'$gt': time_section[0], '$lt': time_section[1]} 
		

		# Max strategy
		# return max data in each time step section.
		reduce_max = """
			function(obj, prev){
				if (prev.time == 0)
					prev.time = parseInt(obj.time/%d)*%d
				if (prev.value < obj.metrics['%s'])
					prev.value = obj.metrics['%s']
			}
		""" % (step, step, metric, metric)
		#print reduce_max


		# Read data from database
		ret = host_coll.group("function (x) { return {'index': parseInt(x.time/%d)}; }" % step,
					{'time': time_filter}, 
					{'time': 0, 'value': 0}, 
					reduce_max,
					"function (doc) { delete doc.index; }")

		return ret

	def remove_host(self, hosts):
		self.agent_set = self.get_hosts()
		count = 0

		connection = pymongo.Connection(*self.hostaddr)
		db = connection[self.dbname]

		for host in hosts:
			if host in self.agent_set:
				try:
					db[self.metadata].remove({'flag': 'host', 'name': host})
					db[host].drop()
				except Exception, e:
					pass
				else:
					count += 1
		
		return count		
					
	def dump_metric(self, hosts, time_section=None, step=30):
		connection = pymongo.Connection(*self.hostaddr)
		db = connection[self.dbname]
		def getlast(host_coll):
			return host_coll.find({}, {'time': 1}).sort("time", pymongo.DESCENDING).limit(1)

		ret = {}
		for host in hosts:
			host_coll = db[host]

			# Get last docment in specified collection.
			if not time_section:
				time_section = (-step, None)

			# If start time of time section is negitive, get data from tail of collection.
			if time_section[0] < 0:
				last_time = getlast(host_coll)
				if last_time.count():
					time_filter = {'$gt': int(last_time[0]['time']/step)*step + time_section[0] + step}
				else:
					continue
			# Otherwise get data normally.
			else:
				time_filter = {'$gt': time_section[0], '$lt': time_section[1]} 

			ret[host] = list(host_coll.find({'time': time_filter}))
		return ret


	#new function
	def get_metrics_name(self):
		conn = pymongo.Connection(*self.hostaddr)
		db = conn[self.dbname]
		col = db[self.metadata]
		one = col.find_one()
		if (len(one) > 0):
			return one["metrics"].keys()
		else:
			return None


	def get_metric_aver_and_max(self, host, metric, time_section=None, step=30):
		result = []
		total = 0.0
		n = 0
		max = 0.0
		timestamp_for_max = 0.0
		if time_section != None:
			result = self.get_metric(host, metric, (date_to_stamp(time_section[0]), date_to_stamp(time_section[1])), step)
		else:
			result = self.get_metric(host, metric, None, step)
		for item in result:
			item_value = float(item['value'])
			total += item_value
			if max <= item_value:
				max = item_value
				timestamp_for_max = item['time']
			n += 1
		#print total, n
		if n == 0:
			return None
		return (total / n, max, timestamp_for_max)


	def get_metrics_value(self, host, metrics_name, time_section = None, step = 30):
		metrics_value = {}
		for metric in metrics_name:
			#print metric
			result = self.get_metric_aver_and_max(host, metric, time_section, step)
			if result != None:
				metrics_value[metric] = {'aver': result[0], 'max': result[1], 'max_time': result[2]}
		return metrics_value


	def get_hosts(self):
		"""
		Get all names of hosts stored in database.

		:returns: names of hosts, list
		"""

		connection = pymongo.Connection(*self.hostaddr)
		db = connection[self.dbname]
		metadata = db[self.metadata]

		ret = metadata.find({'flag': 'host'})
		hosts = map(lambda x:x['name'], ret)

		return hosts


	def get_hosts(self, type='physical'):
		'''
			Get all physical hosts' name
		'''
		connection = pymongo.Connection(*self.hostaddr)
		db = connection[self.dbname]
		metadata = db[self.metadata]

		ret = metadata.find({'flag': 'host', 'type' : type})
		hosts = map(lambda x:x['name'], ret)

		return hosts


def date_to_stamp(dt):
	if re.match(ur"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", dt):
		#time.strptime(dt, '%Y-%m-%d %H:%M:%S')
		s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
	elif re.match(ur"\d{4}-\d{2}-\d{2}", dt):
		dt += " 00:00:00"
		s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
	return int(s)


if __name__=="__main__":
	meta_db = MongoDB(("127.0.0.1", 27017), "monitor_fine_grained", "metadata")
	
	hosts = meta_db.agent_set
	for host in hosts:
		host_db = MongoDB(("127.0.0.1", 27017), "monitor_fine_grained", host)
		metrics_name = host_db.get_metrics_name()
		print host_db.get_metrics_value(host, metrics_name, ('2013-10-01', '2013-10-26'), 30)
		#print host_db.get_metric(host, "sr0-wrqmps", (date_to_stamp('2013-10-01 00:00:00'), date_to_stamp('2013-10-26 00:00:00')), 30)
		#print host_db.get_metric_aver_and_max(host, "mem_free", ('2013-10-01', '2013-10-26'), 30)
	#print meta_db.date_to_stamp('2013-10-07 00:00:00')
	
	# print db.get_host("one-10")
	# print db.get_host("127.0.0.1")
	#print db.get_hosts()
	#for i in  db.dump_metric('12184', (-5, None), step=5):
	#	print i
	#print db.remove_host(['9788','9789'])
	#for i in db.get_metric('one-10', 'cpu_usage', (-3600, None)):
	#	print i
	#print '1297' in db.agent_set
	#db.clearall()
