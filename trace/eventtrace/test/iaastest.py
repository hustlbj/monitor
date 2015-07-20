from IaaSAPI import IaaSAPI
import time
import random
import json

conf={}
conf["DIRECT_EXCHANGE"] = "call_direct_topic"
conf["TOPIC_EXCHANGE"] = "service_call_topic"
conf["RPC_EXCHANGE"] = "service_cast_topic"

NUM = 1

iaas_api = IaaSAPI(conf,'iaas_api')

ch={ 'user':'test','memory':'256','vcpu':'1','img':'centos-5.5-x86_64','count':1,'flag':'iaas','key':'default' }

def vmcreate_test():
    result = []
    d_result = []
    for i in range(NUM):
        ts = time.time()
        ret = iaas_api.vm_create(ch)
        te = time.time()
        ret = json.loads(ret)
        if ret[0]:
            result.append(te-ts)
            vmid = ret[1][0][0]
            ts = time.time()
            iaas_api.vm_delete('test', vmid)
            te = time.time()
            d_result.append(te-ts)
        time.sleep(0.1)
    s = 0
    c = 0
    for i in result:
        if i<1:
            s+=i
            c+=1
    print c, s/c
    s = 0
    c = 0
    for i in d_result:
        if i<1:
            s+=i
            c+=1
    print c, s/c
    print

#vmcreate_test()
############################################
def call_api(func, *args, **kargs):
    result = []
    d_result = []
    p_func = getattr(iaas_api, func)
    for i in range(NUM):
        ts = time.time()
        ret = p_func(*args, **kargs)
        te = time.time()
        ret = json.loads(ret)
	print ret
        if ret[0]:
            result.append(te-ts)
        time.sleep(0.1)
    s = 0
    c = 0
    for i in result:
        if i<1:
            s+=i
            c+=1
    print func
    print c, s/c
    print

#call_api("get_hostpool_info")
call_api("get_user_list")
#call_api("get_vmpool_info", 'test')
#call_api("querykeys", 'test')
#call_api("get_imagepool_info", 'test')


