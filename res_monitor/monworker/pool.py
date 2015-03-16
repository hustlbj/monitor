#!/usr/bin/env python

import threading
import copy

class NoLock(object):
	"""
	NoLock
	"""

	def __enter__(self):
		pass

	def __exit__(self, e_t, e_v, t_b):
		pass



class MetricPool(object):
	"""
	MetricPool stored fixed metric data.
	"""

	def __init__(self, lock=False):
		super(MetricPool, self).__init__()
		self._pool = {}

		# Using RLock if pool related to multi-thread
		if lock:
			self._lock = threading.RLock()

		# Using NoLock if related to single-thread
		else:
			self._lock = NoLock()


	def dump(self):
		"""
		Dump all metric data from pool and clear pool.

		:returns: all metric data in pool, string 
		"""

		with self._lock:
			data = str(self._pool)
			for key, val in self._pool.items():
				print key, len(val)
			self._pool = {}

		return data


	def insert(self, host, data):
		"""
		Insert metric data into sepecifical host object.

		:param host: name of host
		:param data: metric data
		"""

		with self._lock:
			# If host doesnt in the pool, add it into pool
			if not self._pool.has_key(host):
				self._pool[host] = []

			# Insert data into pool
			self._pool[host].append(data)


	def remove(self, host):
		"""
		"""
		pass


	def show(self):
		"""
		Print all data in pool
		"""
		return self._pool



# class MetricPool(object):
# 	"""docstring for MetricPool"""
# 	def __init__(self, lock=False):
# 		super(MetricPool, self).__init__()
# 		self._pool = {}
# 		self._pool_template = {}
# 		if lock:
# 			self._lock = threading.RLock()
# 		else:
# 			self._lock = NoLock()

# 	def dump(self):
# 		with self._lock:
# 			data = str(self._pool)
# 			self._pool = copy.deepcopy(self._pool_template)

# 		return data

# 	def insert(self, host, raw_data):
# 		if type(raw_data) == str:
# 			raw_data = eval(raw_data)
# 		timestamp = raw_data[0]
# 		data = raw_data[1]
# 		with self._lock:
# 			# If host doesnt in the pool, add it into pool and pool_template
# 			if not self._pool_template.has_key(host):
# 				host_template = {}
# 				for metric, metric_val in data.items():
# 					host_template[metric] = []
# 				self._pool_template[host] = host_template
# 				self._pool[host] = copy.deepcopy(host_template)

# 			# Insert data into pool
# 			for metric, metric_val in data.items():
# 				self._pool[host][metric].append((timestamp, metric_val))

# 	def remove(self, host):
# 		with self._lock:
# 			if self._pool_template.has_key(host):
# 				del self._pool_template.pop[host]


# 	def show(self):
# 		return self._pool, self._pool_template



# Another version with structure of pool as following:
# 	{
# 		"one-123":[
# 			(timestamp1, {"cpu*cpu_user": xxx, ...}),
# 			(timestamp2, {"cpu*cpu_user": xxx, ...}),
# 			...
# 		],
# 		"one-540":[
# 			(timestamp1, {"cpu*cpu_user": xxx, ...}),
# 			(timestamp2, {"cpu*cpu_user": xxx, ...}),
# 			...
# 		],
# 		...
# 	}

