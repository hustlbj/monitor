from IaaSAPI import IaaSAPI
import time
import random
import json

conf={}
conf["DIRECT_EXCHANGE"] = "call_direct_topic"
conf["TOPIC_EXCHANGE"] = "service_call_topic"
conf["RPC_EXCHANGE"] = "service_cast_topic"

NUM = 200

iaas_api = IaaSAPI(conf,'iaas_api')

ch={ 'user':'test','memory':'256','vcpu':'1','img':'centos-5.5-x86_64','count':1,'flag':'iaas','key':'testkey1' }
#ts = time.time()
#ret = iaas_api.vm_create(ch)
#te = time.time()
#print 'vm_create:', te - ts
#print

ts = time.time()
ret = iaas_api.get_user_list()
te = time.time()
print 'get_user_list:', te - ts
print 'result:', ret
print

ts = time.time()
ret = iaas_api.get_auth('test')
te = time.time()
print 'get_auth:', te - ts
print 'result:', ret
print 

#for j in range(1):
#    result = []
#    d_result = []
#    for i in range(NUM):
#        ts = time.time()
        #iaas_api.get_vmpool_info('test')
        #ret = iaas_api.get_hostpool_info()
#        ret = iaas_api.vm_create(ch)
#        te = time.time()
#        ret = json.loads(ret)
#        if ret[0]:
#            result.append(te-ts)
#            vmid = ret[1][0][0]
##            ts = time.time()
#            iaas_api.vm_delete('test', vmid)
#            te = time.time()
#            d_result.append(te-ts)
#        time.sleep(0.1)
#    s = 0
#    c = 0
#    for i in result:
#        if i<1:
#            s+=i
#            c+=1
#    print c, s/c
#    s = 0
#    c = 0
#    for i in d_result:
#        if i<1:
#            s+=i
#            c+=1
#    print c, s/c
#    print
############################################
for j in range(1):
    result = []
    d_result = []
    for i in range(NUM):
        ts = time.time()
        #iaas_api.get_vmpool_info('test')
        ret = iaas_api.get_hostpool_info()
        #ret = iaas_api.vm_create(ch)
        te = time.time()
        ret = json.loads(ret)
        if ret[0]:
            result.append(te-ts)
        time.sleep(0.1)
    s = 0
    c = 0
    for i in result:
        if i<1:
            s+=i
            c+=1
    print "get_hostpool_info"
    print c, s/c
    print

for j in range(1):
    result = []
    d_result = []
    for i in range(NUM):
        ts = time.time()
        ret = iaas_api.get_vmpool_info('test')
        te = time.time()
        ret = json.loads(ret)
        if ret[0]:
            result.append(te-ts)
        time.sleep(0.1)
    s = 0
    c = 0
    for i in result:
        if i<1:
            s+=i
            c+=1
    print "get_vmpool_info"
    print c, s/c
    print

for j in range(1):
    result = []
    d_result = []
    for i in range(NUM):
        ts = time.time()
        ret = iaas_api.get_user_list()
        te = time.time()
        ret = json.loads(ret)
        if ret[0]:
            result.append(te-ts)
        time.sleep(0.1)
    s = 0
    c = 0
    for i in result:
        if i<1:
            s+=i
            c+=1
    print "get_user_list"
    print c, s/c
    print
for j in range(1):
    result = []
    d_result = []
    for i in range(NUM):
        ts = time.time()
        ret = iaas_api.querykeys('test')
        te = time.time()
        ret = json.loads(ret)
        if ret[0]:
            result.append(te-ts)
        time.sleep(0.1)
    s = 0
    c = 0
    for i in result:
        if i<1:
            s+=i
            c+=1
    print "querykeys"
    print c, s/c
    print

for j in range(1):
    result = []
    d_result = []
    for i in range(NUM):
        ts = time.time()
        ret = iaas_api.get_imagepool_info('test')
        te = time.time()
        ret = json.loads(ret)
        if ret[0]:
            result.append(te-ts)
        time.sleep(0.1)
    s = 0
    c = 0
    for i in result:
        if i<1:
            s+=i
            c+=1
    print "get_imagepool_info"
    print c, s/c
    print

