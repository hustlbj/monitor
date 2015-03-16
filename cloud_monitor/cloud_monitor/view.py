import json
from django.http import HttpResponse
from django.shortcuts import render_to_response
from resMonitor import resMonAPI
from compMonitor import cmMonAPI
from resMonitor import schedAPI
import os.path as path
import time

hostaddr = ('192.168.1.146', 27017)
statistics_db = 'monitor_statistics'
statistics_col = 'cluster_info'
fine_grained_db = 'monitor_fine_grained'
fine_metadata_col = 'metadata'
cluster = ''
year = time.localtime(time.time())[0]
month = time.localtime(time.time())[1]
host = ''
metric_name = ''
metric_mode = 'aver'

def monitor(request):
	return render_to_response('monitor.html', {})

def get_home(request):
	return render_to_response('global.html', {})

def get_resource(request):
	return render_to_response('resource.html', {})

def get_components(request):
	return render_to_response('components.html', {})

def get_clusters_info(request):
	api = schedAPI.SchedAPI(hostaddr, statistics_db)
	clusters_info = api.get_clusters_statistics(statistics_col)
	print clusters_info
	return HttpResponse(json.dumps(clusters_info))

def get_cluster_info(request):
	cluster = request.POST.get('cluster', '')
	api = schedAPI.SchedAPI(hostaddr, statistics_db)
	cluster_info = api.get_cluster_statistics(statistics_col, cluster)
	if cluster_info != None:
		return HttpResponse(json.dumps(cluster_info))
	else:
		return HttpResponse(json.dumps({}))

def glo_get_host_list(request):
	host_list = []
	cluster = request.POST.get('cluster', '')
	api = schedAPI.SchedAPI(hostaddr, cluster)
	metadata = api.get_host_metadata(None, None)
	if metadata != None:
		for meta in metadata:
			simple_info = schedAPI.get_simple_info(meta)
			host_list.append({'name': meta['name'], 'type': meta['type'],\
			'mem_total': simple_info[0], 'cpu_num': simple_info[1],\
			'cpu_MHz': simple_info[2], 'cache_size': simple_info[3],\
			'day': time.strftime("%Y-%m-%d", time.localtime(meta['day']))})
	return HttpResponse(json.dumps(host_list))

def res_get_host_list(request):
	host_type = request.POST.get('host_type', '')
	meta_db = resMonAPI.MongoDB(hostaddr, fine_grained_db, fine_metadata_col)
	hosts_list = meta_db.get_host_list(meta_db.agent_set, host_type)
	hosts_list_new = []
	now_time = int(time.time())
	for host in hosts_list:
		if now_time - int(host['time']) < 45:
			host['stat'] = 'on'
		elif now_time - int(host['time']) < 90:
			host['stat'] = 'lost'
		else:
			host['stat'] = 'off'
		hosts_list_new.append(host)
	print hosts_list_new
	return HttpResponse(json.dumps(hosts_list_new))

def res_get_host_metadata(request):
	host = request.POST.get('host', '')
	meta_db = resMonAPI.MongoDB(hostaddr, fine_grained_db, fine_metadata_col)
	metadata_dict = {}
	if host != '':
		metadata_dict = meta_db.get_host_detail(host)
	return HttpResponse(json.dumps(metadata_dict))

def res_get_host_metric(request):
	metric_value = []
	host = request.POST.get('host', '')
	group = request.POST.get('group', '')
	metric = request.POST.get('metric', '')
	step = int(request.POST.get('step', '30'))
	all_metrics = []
	fixed_metric = []
	if group != '' and metric != '':
		host_db = resMonAPI.MongoDB(hostaddr, fine_grained_db, fine_metadata_col)
		all_metrics = host_db.get_metric_names(host)
		for one in all_metrics:
			if one == metric or one.find('-' + metric, 0) > 0:
				fixed_metric.append(one)
		for one in fixed_metric:
			value = host_db.get_metric(host, one, None, step)
			if value and len(value) > 0:
				tmp_list = []
				time_list = []
				for v in value:
					tmp_list.append(v["value"])
					time_list.append(v["time"])
				metric_value.append({'name': one, 'data': tmp_list, 'time': time_list})
	return HttpResponse(json.dumps(metric_value))

def get_host_metadata(request):
	host = request.POST.get('host', '') 
	cluster = request.POST.get('cluster', '') 
	api = schedAPI.SchedAPI(hostaddr, cluster)
	metadata = api.get_host_metadata(host, None)
	if metadata == None:
		metadata = {}
	else:
		metadata = schedAPI.get_metadata(metadata[0])
	return HttpResponse(json.dumps(metadata))

def get_host_metrics(request):
	metrics_value = {}
	metrics_tmp = []
	cluster = request.POST.get('cluster', '')
	host = request.POST.get('host', '')
	metric_name = request.POST.get('metric', '')
	metric_mode = request.POST.get('mode', 'both')
	start = request.POST.get('start', '')
	end = request.POST.get('end', '')
	api = schedAPI.SchedAPI(hostaddr, cluster)
	metadata = api.get_host_metadata(host, None)
	if metadata != None and len(metadata) > 0:
		if metadata[0]['type'] == 'physical':
			host = 'p_' + host
		else:
			host = 'v_' + host
#		api.get_timesection(year, month)
		api.start, api.end = start, end
		try:
			cursor = api.get_metrics_day_to_day(host, api.start, api.end, None)
			metrics_tmp = [cursor[i] for i in range(cursor.count())]
			metrics_value = schedAPI.get_metrics(metrics_tmp, api.start, api.end, metric_name, metric_mode)
		except Exception:
			pass
	else:
		pass
	metrics_tmp = []
	for key in metrics_value.keys():
		metrics_tmp.append({'name': key, 'data': metrics_value[key]})
	return HttpResponse(json.dumps(metrics_tmp))


def get_all_recent_data(request):
	if request.method == 'POST' and request.is_ajax():
		api = cmMonAPI.CompMonAPI()
		return HttpResponse(json.dumps(api.getAllStat()))
	else: 
		return render_to_response('error.html', {})


def get_one_recent_data(request):
	groupName = request.GET.get('group', '')
	if groupName != '':
		api = cmMonAPI.CompMonAPI()
		return HttpResponse(json.dumps(api.getOneStat(groupName)))
	else:
		return HttpResponse(json.dumps({}))

def get_one_fsm(request):
	groupName = request.GET.get('group', '')
	startTime = request.GET.get('start', '')
	endTime = request.GET.get('end', '')
	if groupName != '':
		api = cmMonAPI.CompMonAPI()
		return HttpResponse(json.dumps(api.getGroupFSM(groupName, startTime, endTime)))
	else:
		return HttpResponse(json.dumps([]))

def comp_get_fsms(request):
	#systems = {}
	systems = []
	api = cmMonAPI.CompMonAPI()
	all_groups = api.getAllCompsName()
	if all_groups:
		for group in all_groups:
			one_stat = api.getOneStat(group)
			detail = api.getGroupFSM(group, None, None)
			if len(detail) > 12:
				detail = detail[-12:]
			one_stat["detail"] = detail
			#systems[group] = one_stat
			systems.append(group)
			systems.append(one_stat)
	print systems
	return HttpResponse(json.dumps(systems))
	

def get_metrics_report(request):
	metrics_tmp = []
	cluster = request.POST.get('cluster', '')
	host = request.POST.get('host', '')
	metric_mode = request.POST.get('mode', 'aver')
	start = request.POST.get('start', '')
	end = request.POST.get('end', '')
	api = schedAPI.SchedAPI(hostaddr, cluster)
	metadata = api.get_host_metadata(host, None)
	if metadata != None and len(metadata) > 0 and metric_mode != 'both':
		if metadata[0]['type'] == 'physical':
			host = 'p_' + host
		else:
			host = 'v_' + host
		api.start, api.end = start, end
		try:
			cursor = api.get_metrics_day_to_day(host, api.start, api.end, None)
			metrics_tmp = [cursor[i] for i in range(cursor.count())]
			return HttpResponse(json.dumps(schedAPI.get_report(metrics_tmp, metric_mode)))
		except Exception, e:
			print str(e)
			return HttpResponse(json.dumps(metrics_tmp))
	else:
		return HttpResponse(json.dumps(metrics_tmp))

