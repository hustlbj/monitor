
import time
import json
import random
import pprint
from IaaSAPI import IaaSAPI

conf={}
conf["DIRECT_EXCHANGE"] = "call_direct_topic"
conf["TOPIC_EXCHANGE"] = "service_call_topic"
conf["RPC_EXCHANGE"] = "service_cast_topic"

iaas_api = IaaSAPI(conf,'iaas_api')


ch={ 'user':'test','memory':'512','vcpu':'2','img':'CentOS-5.5-x86_64','count':1,'flag':'iaas','key':'default' }

LIST = { 
#  "querykeys": ('test',),
  "get_hostpool_info": (), 
#  "get_host_info": (47,),
  "get_user_list": (), 
  "get_vmpool_info": ('test',), 
#  "get_imagepool_info": ('test',),
#  "get_image_info": ('test',),
#  "get_vms_info": (),
#  "get_vm_status": ("10374",),
#  "get_vm_info": ("100",),
#  "get_vm_ip": ("100",)
}

COUPLE = [
#  ('vm_create', 'vm_delete'), 
#  ('user_create', 'user_delete'), 
  ('usercreatekeys', 'userdelkeys'),
] 

def generate_oplist(n, m):
    oplist = []
    for key in LIST.keys():
        oplist += [key] * n

    random.shuffle(oplist)

    
    for op1,op2 in COUPLE:
        temp = random.sample(range(len(oplist)), m)
        temp.sort()
        for i in temp:
            oplist.insert(i, op1)
            oplist.insert(i+5, op2)


    return oplist

def test():
    for key,val in LIST.items():
        func = getattr(iaas_api, key)
        print type(func(*val))


def experiment(oplist):

    result = {}
    vms = []
    keys = []
    users = []

    total_start = time.time()

    for op in oplist:
        if not result.has_key(op):
            result[op] = {True: [], False: []}

        if op == 'vm_create':
            tstart = time.time()
            ret = json.loads(iaas_api.vm_create(ch))
            tend = time.time()
            if ret[0] == True:
                vms.append(ret[1][0][0])
            else:
                vms.append('-1') 
            result[op][ret[0]].append(tend-tstart)

        elif op == 'vm_delete':
            tstart = time.time()
            ret = json.loads(iaas_api.vm_delete('test', vms.pop()))
            tend = time.time()
            result[op][ret[0]].append(tend-tstart)

        elif op == 'usercreatekeys':
            keyname = 'chriskeys%d' % oplist.index(op)
            tstart = time.time()
            ret = json.loads(iaas_api.usercreatekeys('test', keyname))
            tend = time.time()
            if ret[0] == 0:
                keys.append(keyname)
                result[op][True].append(tend-tstart)
            else:
                result[op][False].append(tend-tstart)
                keys.append('-1')

        elif op == 'userdelkeys':
            tstart = time.time()
            ret = json.loads(iaas_api.userdelkeys('test', keys.pop()))
            tend = time.time()
            stat = not bool(ret[0])
            result[op][stat].append(tend-tstart)

        elif op == 'user_create':
            username = 'chris%d' % oplist.index(op)
            tstart = time.time()
            ret = json.loads(iaas_api.user_create(username))
            tend = time.time()
            if ret[0] == True:
                users.append(username)
            else:
                users.append('-1')
            result[op][ret[0]].append(tend-tstart)

        elif op == 'user_delete':
            tstart = time.time()
            ret = json.loads(iaas_api.user_delete(users.pop()))
            tend = time.time()
            result[op][ret[0]].append(tend-tstart)

        else:
            func = getattr(iaas_api, op)
            val = LIST[op]
            tstart = time.time()
            ret = json.loads(func(*val))
            tend = time.time()
            if op == 'get_vm_ip':
                result[op][True].append(tend-tstart)
            else:
                result[op][ret[0]].append(tend-tstart)

        print op, ret[0]
        time.sleep(0.1)
              
    total_end = time.time()

    pprint.pprint(result)    
#    f = open('report', 'w')
#    print >> f, total_start, total_end
#
#    for key, val in result.items():
#        print >> f, key
#        print >> f, val[True]  
#        print >> f, val[False]  
#        print >> f, ''
#
#    f.close()

if __name__=="__main__":
    #print json.loads(iaas_api.vm_delete('test', '-1'))
    #print json.loads(iaas_api.user_delete('-1'))
    #print json.loads(iaas_api.userdelkeys('test', '-1'))
    #print json.loads(iaas_api.querykeys('test'))
    #print json.loads(iaas_api.usercreatekeys('test', "test_chris_1"))
    #print json.loads(iaas_api.userdelkeys('test', "test_chris_1"))
    #from oplist import oplist
    #oplist = generate_oplist(0,2)
    oplist = ['usercreatekeys', 'userdelkeys']*150
    experiment(oplist)
