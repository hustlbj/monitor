#!/usr/bin/env python

import pymongo
import time
import re
import os.path as path
import sys, getopt
from include.configobj import ConfigObj


CURDIR = path.dirname(path.abspath(__file__))

class SchedAPI(object):

	def __init__(self, hostaddr, dbname):
		self.hostaddr = hostaddr
		self.dbname = dbname
		self.agent_set = self.__get_agents()
		self.start = ''
		self.end = ''
		self.metric_description = self.__get_metric_description()


	def __get_agents(self):
		self.agent_set = []
		try:
			conn = pymongo.Connection(*self.hostaddr)
			db = conn[self.dbname]
			self.agent_set = db.collection_names()
			self.agent_set.remove('system.indexes')
			self.agent_set.remove('metadata')
		except Exception, e:
			pass
		return self.agent_set


	def get_timesection(self, year, month):
		days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
		if (year % 4 == 0) or ((year % 100 == 0) and (year % 400 == 0)):
			days[1] = 29
		self.start = str(year) + '-' + str(month) + '-' + '1'
		self.end = str(year) + '-' + str(month) + '-' + str(days[month - 1])
		return (self.start, self.end)


	def get_cluster_statistics(self, collection, cluster):
		try:
			conn = pymongo.Connection(*self.hostaddr)
			db = conn[self.dbname]
			cursor = db[collection].find({'cluster': cluster}, {'_id': 0})
			if cursor != None and cursor.count() > 0:
				return cursor.next()
			else:
				return None
		except pymongo.errors, e:
			return None
	
	def get_clusters_statistics(self, collection):
		clusters_statistics = []
		try:
			conn = pymongo.Connection(*self.hostaddr)
			db = conn[self.dbname]
			cursor = db[collection].find({}, {'_id': 0})
			if cursor != None and cursor.count() > 0:
				for i in range(cursor.count()):
					clusters_statistics.append(cursor.next())
		except pymongo.errors, e:
		   pass
		return clusters_statistics


	#return None ot pymongo.cursor
	def get_metrics_day_to_day(self, col, start, end, metric_filter = None):
		try:
			conn = pymongo.Connection(*self.hostaddr)
			db = conn[self.dbname]
			self.start = start
			self.end = end
			start_t = date_to_stamp(start)
			end_t = date_to_stamp(end)
			if end == 0:
				end = time.time()
			if metric_filter == None:
				return db[col].find({'day': {'$gte': start_t, \
					'$lte': end_t}}, {'_id': 0}).sort([('day', pymongo.ASCENDING)])
			else:
				metric_filter = 'value.' + metric_filter
				return db[col].find({'day': {'$gte': start_t, \
					'$lte': end_t}}, {'_id': 0, 'day': 1, metric_filter: 1})\
					.sort([('day', pymongo.ASCENDING)])
		except pymongo.errors, e:
			return None


	def get_metrics_a_day(self, col, day, metric_filter):
		cursor = self.get_metrics_day_to_day(col, str(day), str(day), metric_filter)
		if cursor != None and cursor.count() > 0:
			return cursor[0]
		else:
			return None


	def get_metrics_a_month(self, col, year, month, metric_filter):
		section = self.get_timesection(year, month)
		cursor = self.get_metrics_day_to_day(col, section[0], section[1], metric_filter)
		if cursor != None and cursor.count() > 0:
			num = cursor.count()
			metrics = [cursor[i] for i in range(num)]
			#for i in range(cursor.count()):
			#    metrics.append(cursor[i])
			return metrics
		else:
			return None


	def get_aver_day_to_day(self, col, start_t, end_t):
		cursor = self.get_metrics_day_to_day(col, start_t, end_t)
		if cursor != None and cursor.count() > 0:
			all_metrics = []
			for i in cursor.count():
				all_metrics.append(cursor[i])
			return metrics
		else:
			return None
		aver_metrics = {}
		for metric in all_metrics:
			for key in metric:
				if key in aver_metrics.keys():
					aver_metrics[key] += metric[key]
				else:
					aver_metrics[key] = metric[key]
		num = len(all_metrics)
		for key in aver_metrics.keys():
			aver_metrics[key] /= num
		return aver_metrics


	def get_hosts(self, type = None):
		if type == None:
			return self.agent_set
		elif type == 'physical':
			return [x for x in self.agent_set if re.match(u"^p_", x)]
		else:
			return [x for x in self.agent_set if re.match(u"^v_", x)]


	def get_host_metadata(self, host_name, type_filter, collection = 'metadata'):
		try:
			conn = pymongo.Connection(*self.hostaddr)
			db = conn[self.dbname]
			col = db[collection]
			if host_name == None or host_name == '':
				if type_filter == None:
					cursor = col.find({}, {'_id': 0}).sort([("type", 1), ("name", 1)])
				else:
					cursor = col.find({'type': type_filter}, {'_id': 0}).sort([("name", 1)])
			else:
				cursor = col.find({'name': host_name}, {'_id': 0})
			if cursor.count() > 0:
				meta_list = []
				for i in range(cursor.count()):
					meta_list.append(cursor.next())
				return meta_list
			else :
				return None
		except Exception, e:
			return None


	def __get_metric_description(self):
		return ConfigObj(CURDIR+path.sep+'metric.description')


def date_to_stamp(dt):
	if re.match(ur"\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}", dt):
		#time.strptime(dt, '%Y-%m-%d %H:%M:%S')
		s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
	elif re.match(ur"\d{4}-\d{1,2}-\d{1,2}", dt):
		dt += " 00:00:00"
		s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
	else:
		s = 0
	return int(s)


def print_metadata(meta):
	print '|', meta['name'].ljust(96), '|'
	print '|', ('Memory total size: ' + str(meta['info']['mem_total']) + ' KB').center(96), '|'
	print '|', ('CPU nums: ' + str(meta['info']['cpu']['cpu_num']) + \
				'   width: ' + str(meta['info']['cpu']['width']) + \
				'   frequency: ' + str(meta['info']['cpu']['cpu_MHz'] + ' MHz') + \
				'   cache size' + str(meta['info']['cpu']['cache_size'])).center(97) + '|'
	disks = [{x: meta['info']['disks'][x]['partitions']} for x in meta['info']['disks']]

	disk_msg = 'Disks: '.center(97) + '|'
	for disk in disks:
		key = disk.keys()[0]
		disk_msg += ('\n|' + '\t' + key + ' partitions:  ').ljust(94) + '|'
		for part in disk[key]:
			try:
				disk_msg += '\n|' + ('\t\t' + part + ': available ' + str(disk[key][part]['avail']) \
				+ 'KB  used ' + str(disk[key][part]['used']) + 'KB  ').ljust(85) + '|'
			except KeyError:
				disk_msg += '\n|' + ('\t\t' + part + ': size ' + str(disk[key][part]['size']) + 'KB  ').ljust(85) + '|'
			else:
				pass
	print '|', disk_msg.center(96)

	networks = [{x: meta['info']['network_interfaces'][x]} for x in meta['info']['network_interfaces']]
	net_msg = 'Network: '.center(97) + '|'
	for net in networks:
		key = net.keys()[0]
		net_msg += '\n|' + ('\t\t' + key + ': hard_addr ' + net[key]['hwaddr']\
					+ '  scope ' + net[key]['scope']).ljust(85) + '|'
	print '|', net_msg


def get_metadata(meta):
	return meta['info']


def print_simple(meta):
	print ('|' + '%s    Memory: %dKB  CPU: %dcores, %sMHz, %s cache'.ljust(72) +'|') \
			% (meta['name'], meta['info']['mem_total'], meta['info']['cpu']['cpu_num'],\
			meta['info']['cpu']['cpu_MHz'], meta['info']['cpu']['cache_size'])

def get_simple_info(meta):
	return (meta['info']['mem_total'], meta['info']['cpu']['cpu_num'], \
			meta['info']['cpu']['cpu_MHz'], meta['info']['cpu']['cache_size'])


def print_metrics(metrics_value, start, end, metric_name):
	start_t = date_to_stamp(start)
	end_t = date_to_stamp(end)
	i = 0
	print_str = ''
	while start_t <= end_t:
		if i < len(metrics_value):
			value = metrics_value[i]
			if value['day'] == start_t:
				print_str += '|' + str(value['value'][metric_name]['aver'])
				i += 1
			else:
				print_str += '|*'
		else:
			print_str += '|*'
		start_t += 86400
	print '|' + (print_str + '|').center(98) + '|'


def get_fixed_metric_name(metric_value, metric_name):
	fixed_names = []
	for key in metric_value.keys():
		if key == metric_name or key.find('-' + metric_name, 0) > 0:
			fixed_names.append(key)
	return fixed_names

#params: metrics_value=[{'day':xxx, 'value': {'cpu':1, 'mem':2, }, ...}, {}, ...]
#return {key1:[1,2,3,..], key2:[1,2,3,...],...}
def get_metrics(metrics_value, start, end, metric_name, mode='aver'):
	metrics = {}
	if metrics_value != None and len(metrics_value) > 0:
		fixed_names = get_fixed_metric_name(metrics_value[0]['value'], metric_name)
	else:
		return metrics
	start_t = date_to_stamp(start)
	end_t = date_to_stamp(end)
	i = 0

	#print metrics

	if mode == 'aver' or mode == 'max':
		for key in fixed_names:
			metrics[key + '_' + mode] = []
		while start_t <= end_t:
			if i < len(metrics_value):
				if metrics_value[i]['day'] == start_t:
					try:
						for key in fixed_names:
							metrics[key + '_' + mode].append(metrics_value[i]['value'][key][mode])
					except KeyError:
						metrics[key + '_' + mode].append(0)
					i += 1
				else:
					metrics[key + '_' + mode].append(0)
			else:
				metrics[key + '_' + mode].append(0)
			start_t += 86400
#	elif mode == 'max':
#		while start_t <= end_t:
#			if i < len(metrics_value):
#				try:
#					if metrics_value[i]['value'][key]['max_time'] == 0 or \
#					(metrics_value[i]['value'][key]['max_time'] >= start_t \
#						and metrics_value[i]['value'][key]['max_time'] <= start_t + 86400):
#						for key in fixed_names:
#							metrics[key].append(metrics_value[i]['value'][key]['max'])
#						i += 1
#					else:
#						metrics[key].append(0)
#				except KeyError:
#					metrics[key].append(0)
#			else:
#				metrics[key].append(0)
#			start_t += 86400
	else:
		for key in fixed_names:
			metrics[key + '_aver'] = []
			metrics[key + '_max'] = []
		while start_t <= end_t:
			if i < len(metrics_value):
				if metrics_value[i]['day'] == start_t:
					try:
						for key in fixed_names:
							metrics[key + '_aver'].append(metrics_value[i]['value'][key]['aver'])
							metrics[key + '_max'].append(metrics_value[i]['value'][key]['max'])
					except KeyError:
						metrics[key + '_aver'].append(0)
						metrics[key + '_max'].append(0)
					i += 1
				else:
					metrics[key + '_aver'].append(0)
					metrics[key + '_max'].append(0)
			else:
				metrics[key + '_aver'].append(0)
				metrics[key + '_max'].append(0)
			start_t += 86400

	return metrics


def get_report(metrics_value, mode='aver'):
	metrics = []
	values = []
	if metrics_value != None:
		metrics = sorted(metrics_value[0]['value'].keys())
		for item in metrics_value:
			value = []
			for key in metrics:
				value.append(item['value'][key][mode])
			values.append(value)
	print {'metrics': metrics, 'values': values}
	return {'metrics': metrics, 'values': values}
			

def get_fixed_disk_metric(native_metric):
	pass

def get_fixed_net_metric(native_metric):
	pass


def usage():
	print 'usage:'
	print '\t params:'
	print '\t\t -h for help information'
	print '\t\t -c cluster'
	print '\t\t -y year, default this year'
	print '\t\t -m month, default this month'
	print '\t\t -a agent, one physical machine or virtual machine in the cluster'
	print '\t\t -o metric, one metric infomation that you want to look up'
	print '\t\t -v max or aver value'


if __name__ == '__main__':
	hostaddr = ('127.0.0.1', 27017)
	cluster = 'hust'
	year = time.localtime(time.time())[0]
	month = time.localtime(time.time())[1]
	host = ''
	metric_name = ''
	metric_mode = 'aver'

	opts, args = getopt.getopt(sys.argv[1:], 'hc:y:m:a:o:v:')
	if len(opts) < 1:
		print 'Wrong params.'
		usage()
		sys.exit()
	for op, param in opts:
		if op == '-c':
			cluster = param
		if op == '-y':
			year = int(param)
		if op == '-m':
			month = int(param)
		if op == '-a':
			host = param
		if op == '-o':
			metric_name = param
		if op == '-v':
			metric_mode = param
		elif op == '-h':
			usage()
			sys.exit()

	api = SchedAPI(hostaddr, cluster)
	vms = api.get_hosts('virtual')
	pms = api.get_hosts('physical')
	meta_list =  api.get_host_metadata(None, None)
	p_meta_list = [x for x in meta_list if x['type'] == 'physical']
	v_meta_list = [x for x in meta_list if x['type'] == 'virtual']

	time_section = api.get_timesection(year, month)

	print '-'.center(100, '-')
	print '-'.center(100, '-')
	print '|', cluster.center(96), '|'
	print '-'.center(100, '-')
	print '|', api.start.center(46), 'to', api.end.center(46), '|'
	print '-'.center(100, '-')
	print '|', ('physical machines: ' + str(len(pms))).center(46), '|', \
		('virtual machines: ' + str(len(vms))).center(47), '|'
	print '-'.center(100, '-')
	print '-'.center(100, '-')
	print '|', 'physical machines'.center(96), '|'
	print '-'.center(100, '-')
	for meta in p_meta_list:
		#print '|', meta['info'], '|'
		#print_metadata(meta)
		print_simple(meta)
		print '-'.center(100, '-')
	print '-'.center(100, '-')
	print '|', 'virtual machines'.center(96), '|'
	for meta in v_meta_list:
		#print '|', meta['info'], '|'
		#print_metadata(meta)
		print_simple(meta)
		print '-'.center(100, '-')
	print '-'.center(100, '-')
	print 

	if host != '' and metric_name != '':
		try:
			
			print ('%s from %s to %s' % (api.metric_description[metric_name], \
				api.start, api.end)).center(100)
			cursor = api.get_metrics_day_to_day(host, api.start, api.end, None)
			try:
				if cursor.count > 0:
					metrics_value = [cursor.next()]
				print_metrics(metrics_value, api.start, api.end, metric_name)
			except StopIteration:
				print 'agent not found.'
		except KeyError:
			print 'metric does not exist.'
	


