#!/usr/bin/env python
"""
Created on Sep 4,2012

@author LiYC
"""
import os
import time
import net_attach

#from common.default import MODE, ONE_DATA, CONF_DIR, KEY_DIR, KVM_CONF
#from common.default import VM_CONTEXT, VM_CONTEXT_KEY, VM_CONTEXT_FILES
#from common.default import SINGLE_NIC
from vm_content import *

#create the DIR if not exist
if not os.path.isdir(CONF_DIR):
    os.makedirs(CONF_DIR)

def cloud_test():
	print "cloud_test"

def init_conf(f_conf):
    '''initialize the configure file of vms
    '''
    if "memory" not in f_conf:
        f_conf["memory"] = "512"
    if "flag" not in f_conf:
        f_conf["flag"] = "iaas"
    if "vcpu" not in f_conf:
        f_conf["vcpu"] = 1
    #if "cpu" not in f_conf:
    #    f_conf["cpu"] = f_conf["vcpu"]
    if "mode" not in f_conf:
        f_conf["mode"]=MODE
    if "count" not in f_conf:
        f_conf["count"] = 1
    if "type" not in f_conf:
        f_conf["type"] = 1
    if "start" not in f_conf:
        f_conf["start"] = "now"
    if f_conf["start"].upper() == "IMMEDIATE":
        f_conf["start"] = "now"
    elif f_conf["start"].upper() == "BEST_EFFORT":
        f_conf["start"] = "best_effort"
    if f_conf["start"] == "":
        f_conf["start"] = "now"
    if "duration" not in f_conf:
        f_conf["duration"] = "unlimited"
    if f_conf["duration"] == "":
        f_conf["duration"] = "unlimited"
    if "preempt" not in f_conf:
        f_conf["preempt"] = "no"

def create_vm_template(HVM):
    vm_content = None
    print HVM 
    if HVM['flag'] == 'iaas':
        print "iaas"
        if HVM['os'] == 'WINDOWS':
            print "WINDOWS"
            vm_content= WindowsVirtualMachine(SINGLE_NIC)
        else:             
            print "LINUX"
            vm_content = LinuxVirtualMachine(SINGLE_NIC)
    
    else:
        vm_content = LinuxVirtualMachine(SINGLE_NIC)

    vm_content.create(HVM)

    f=os.popen('date +%s')
    DATE=f.readline().strip()
    f.close()
    CONF_FILE=CONF_DIR+os.sep+HVM["user"]+"_"+DATE+".crane"

    try:
        with open(CONF_FILE,"w") as fp:
            fp.write(vm_content.vm.to_content())
        fp.close()
    except EnvironmentError:
        fp.close()
        return None
    return CONF_FILE
"""
def init_vm_context(privatekey, pubkey, user, meepo="none"):
    temp_context_key = [ context_key for context_key in VM_CONTEXT_KEY]
    temp_context_dict = {}
    for dict_key, dict_value in VM_CONTEXT.items():
        temp_context_dict[dict_key] = dict_value
    temp_context_files=""
    temp_context_files= " ".join(VM_CONTEXT_FILES.values())+" "+" ".join([privatekey, pubkey])
    temp_context_files = r'''"%s"'''  % temp_context_files
    temp_context_dict["files"] = temp_context_files
    temp_context_dict["crane_user"] = r'''"%s"'''  %user
    temp_context_dict["meepo"] = r'''"%s"'''  % meepo
    rtl = ",\n".join([ "\t%s = %s"%(key, temp_context_dict[key]) for key in temp_context_key])
    return "CONTEXT = ["+os.linesep+rtl + os.linesep +"]"
    
def create_vm_template(HVM):
    f=os.popen('date +%s')
    DATE=f.readline().strip()
    f.close()
    CONF_FILE=CONF_DIR+os.sep+HVM["user"]+"_"+DATE+".crane"
    if "key" in HVM:
        privatekey=KEY_DIR+"/"+HVM["user"]+"/"+HVM["key"]+"/"+"id_dsa"
        pubkey=KEY_DIR+"/"+HVM["user"]+"/"+HVM["key"]+"/"+"id_dsa.pub"
    else:
        privatekey=""
        pubkey=""
    clone = "yes"
    if int(HVM["type"]) is 0:
        clone = "no"

    meepo = "none"
    if "meepo" in HVM:
        meepo = HVM["meepo"]
    vm_context = init_vm_context(privatekey, pubkey, HVM["user"], meepo)    
    try:
        with open(CONF_FILE,"w") as fp:
            for each in ["name","cpu","memory","vcpu","flag","HOME","key"]:
                if each in HVM:
                    fp.write(each+"="+str(HVM[each])+os.linesep)
            fp.write(KVM_CONF["OS"]+os.linesep)
            fp.write(KVM_CONF["GRAPHICS"]+os.linesep)
            if HVM["flag"] == "iaas":
                fp.write(r'''DISK=[image="'''+HVM["img"]+r'''",driver= "'''+HVM["mode"]+r'''", mode="'''+HVM["mode"]+r'''", target = "vda"]'''+os.linesep)
            if HVM["flag"] == "paas":
                fp.write(r'''DISK=[source="'''+HVM["img"]+r'''",driver= "'''+HVM["mode"]+r'''", mode="'''+HVM["mode"].upper()+r'''", target = "vda"]'''+os.linesep)
            fp.write(KVM_CONF["NETWORK"]+os.linesep)
            fp.write(init_vm_context(privatekey, pubkey, HVM["user"], meepo) + os.linesep)
            sched_str=""
            if "node" in HVM:
                sched_str = r'''REQUIREMENTS = "FREEMEMORY > ''' + str(int(HVM["memory"])*1024) + r''' & HOSTNAME = \"''' + str(HVM["node"]) + '''\""'''+os.linesep+'''RANK = FREEMEMORY''' + os.linesep
            else:
                sched_str = r'''REQUIREMENTS = "FREEMEMORY > ''' + str(int(HVM["memory"])*1024) + '''"'''+os.linesep+'''RANK = FREEMEMORY'''+os.linesep
            fp.write(sched_str)
    except EnvironmentError:
        return None
    return CONF_FILE
"""
def set_mode(mod):
	global MODE
	MODE=mod

def get_vm_ipv6(id):
    '''get the ipv6 address of the vm
    '''
    rls = net_attach.query_ipv6(id)
    if rls[0] == True:
        return rls[1]
    return ""
    
def get_ssh_port(vm_id):
    '''get the local port of ssh fwd
    '''
    rls = net_attach.query_ssh_port(vm_id)
    if rls[0] == True:
        return rls[1]
    return ""
    
def init_vm_data(ip_list, mem, vcpus,key):
    '''init the ipv6 address of the vm
    '''
    if ip_list[0]:
        for each in ip_list[1]:
            cmd_str = "echo \"" + str(each[0]) + "," + str(each[1]) + "," + str(mem) + "," + str(vcpus) +","+str(key)+ "\" >> " + ONE_DATA
            f = os.popen(cmd_str)
            f.close()
            
def get_port(vm_id):
    '''get the vnc port of a vm
    '''
    port = int(vm_id) + 6900
    return port

def get_vm_data(vm_id, list):
    cmd_str = "cat " + ONE_DATA + " | grep ^" + str(vm_id) + ", | cut -d, -f" + str(list)
    f = os.popen(cmd_str)
    data = f.readline().strip()
    f.close()
    return data 

def vm_xml_dict(xml):
    '''change the format of the vms information from xml to dictionary
    '''
    state = ["INIT", "PENDING", "HOLD", "RUNNING", "STOPPED", "SUSPENDED", "DONE", "FAIL"]
    ret = {}
    ret["guid"] = xml.ID
    ret["name"] = xml.NAME
    ret["vcpu"] = xml.TEMPLATE.VCPU
    ret["memory"] = xml.TEMPLATE.MEMORY
    if type(xml.TEMPLATE.NIC) is list:
    	ret["ip"] = xml.TEMPLATE.NIC[0].IP
    else:
        ret["ip"] = xml.TEMPLATE.NIC.IP
    if "IMAGE" in xml.TEMPLATE.DISK:
        ret["image"] = xml.TEMPLATE.DISK.IMAGE
    else:
        ret["image"] = ""
    ret["ipv6"] = get_vm_ipv6(xml.ID)
    if "HISTORY" in xml:
        ret["hostMachine"] = xml.HISTORY.HOSTNAME
    else:
        ret["hostMachine"] = ""
    if int(xml.LCM_STATE) ==  2:
        ret["stat"] = "BOOT"
    else:
        ret["stat"] = state[int(xml.STATE)]
    ret["stime"] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(float(xml.STIME)))
    ret["owner"] = xml.USERNAME
    return ret

##def vm_xml_dict(xml):
##    '''change the format of the vms information from xml to dictionary
##    '''
##    state = ["INIT", "PENDING", "HOLD", "RUNNING", "STOPPED", "SUSPENDED", "DONE", "FAIL"]
##    ret = {}
##    ret["guid"] = xml.ID
##    ret["owner"] = xml.USERNAME
##    if "HISTORY" in xml:
##        ret["hostMachine"] = xml.HISTORY.HOSTNAME
##    else:
##        ret["hostMachine"] = "" 
##    ret["name"] = xml.NAME
##    #ret["cpu"] = (get_vcpus(xml.ID))[1] 
##    ret["cpu"] = get_vm_data(xml.ID, 4)
##    if int(xml.LCM_STATE) ==  2:
##        ret["stat"] = "BOOT"
##    else:
##        ret["stat"] = state[int(xml.STATE)]
##    #ret["memory"] = xml.MEMORY
##    ret["memory"] = get_vm_data(xml.ID, 3)
##    ret["key"]=get_vm_data(xml.ID, 5)
##    ret["vnc_port"] = get_port(xml.ID)
##    #ret["port"] = get_ssh_port(xml.ID)
##    #ret["ip"] = get_vm_ip(xml.ID) 
##    ret["ip"] = get_vm_data(xml.ID, 2) 
##    ret["ipv6"] = get_vm_ipv6(xml.ID) 
##    ret["stime"] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(float(xml.STIME)))
##    return ret
    
def host_xml_dict(xml):
    '''change host info from xml to dict
    '''
    ret = {}
    ret["guid"] = xml.ID
    ret["name"] = xml.NAME
    ret["totalMemory"] = xml.HOST_SHARE.MAX_MEM
    ret["freeMemory"] = xml.HOST_SHARE.FREE_MEM
    #ret["virtualMachines"] = get_vms_host(xml.NAME) 
    ret["virtualMachines"] = xml.HOST_SHARE.RUNNING_VMS 
    ret["totalCpu"] = xml.HOST_SHARE.MAX_CPU
    ret["usedCpu"] = xml.HOST_SHARE.USED_CPU
    ret["state"] = int(xml.STATE)
    return ret
