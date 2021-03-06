import os
import re

from utils import exec_cmd, proc2dict

CPUINFO_PROC = '/proc/cpuinfo'
XEN_PROC = '/proc/xen'
MEMINFO_PROC = '/proc/meminfo'
INTEL_VT = 'Intel_VT'
INTEL_VT_FLAG = 'vmx'
AMD_VT = 'AMD_VT'
AMD_VT_FLAG = 'smx'
XEN_VIRTTYPE = 'xen'
IFCONFIG_PATH = '/sbin/ifconfig'
XM_PATH = 'usr/sbin/xm'
XENTOP_PATH = '/usr/sbin/xentop'

def get_platform_info():

    host = {}
    host['virt_type'] = get_virt_type()
    host['components'] = {}
    host['components']['cpu'] = get_cpu_info()
    host['components']['memory'] = get_mem_info()
    host['components']['filesystem'] = get_disk_info()
    host['components']['network'] = get_network_info()
    host['components']['os'] = get_os_info()
    return host

def get_cpu_info():
    cpuinfopath = CPUINFO_PROC

    fd = open(cpuinfopath)
    cpuinfo = fd.read().strip().split('\n\n')
    fd.close()
    
    cpu = {}
    cpu['cpu_num'] = len(cpuinfo)
    processorinfo = dict([[i.strip() for i in pair] for pair in [l.split(':') \
                          for l in cpuinfo[0].split('\n')]])
    cpu['vendor_id'] = processorinfo['vendor_id']
    cpu['model_name'] = processorinfo['model name']
    cpu['cpu_MHz'] = processorinfo['cpu MHz']
    
    flags = processorinfo['flags'].split()
    if INTEL_VT_FLAG in flags:
        cpu['vt_support'] = INTEL_VT
    elif AMD_VT_FLAG in flags:
        cpu['vt_support'] = AMD_VT
    else:
        cpu['vt_support'] = 'n/a'

    cpu['cache_size'] = processorinfo['cache size']

    cpu['width'] = ('lm' in flags) and 64 or 32
    
    return cpu

def get_virt_type():
    if os.path.exists(XEN_PROC):
        #return XEN_VIRTTYPE
	return ''
    else:
        return ''

def get_mem_info():
    t = get_virt_type()
    if t == '' :
        return get_phy_mem_info()
    else:
        return eval('get_%s_mem_info()' % t)

def get_phy_mem_info():
    fd = open(MEMINFO_PROC)
    memory = {}
    memory['mem_total'] = int(proc2dict(fd)['MemTotal'].split()[0])
    fd.close()
    return memory 

def get_xen_mem_info():
    import XenBroker
    memory = {}
    memory['mem_total'] = XenBroker.get_mem_total(XM_PATH, XENTOP_PATH)
    return memory
    
def get_disk_info():
    disk = { 'local' : {},
             'other' : {} }

    # get info of mounted fs
    import mounts
    mountpoints = mounts.get_all_mountpoints()
    
    # obtain info of all partitions
    import block
    partitions = block.get_all_partitions()
    part_disk = block.get_partition_disk()

    for mp in mountpoints.keys():
        device, fstype, opts = mountpoints[mp]
        if device.startswith('/dev/'):
            device = device.rsplit('/', 1)[-1]
        mp_stat = mounts.get_mp_stat(mp)
        if mp_stat['size'] == 0 or \
           not mounts.is_local_fs(fstype) or \
           device not in part_disk.keys():
            catagory = 'other'
        else:
            catagory = 'local'

        disk[catagory][device] = {}
        disk[catagory][device]['size'] = mounts.myformat(mp_stat['size'], '-k', mp_stat['blocksize'])
        disk[catagory][device]['used'] = mounts.myformat(mp_stat['used'], '-k', mp_stat['blocksize'])
        disk[catagory][device]['avail'] = mounts.myformat(mp_stat['avail'], '-k', mp_stat['blocksize'])
        disk[catagory][device]['on'] = mp

    for partname, partinfo in partitions.items():
        # skip disk
        #if not partname[-1].isdigit() or partname.startswith('loop'):
            #continue
        disk['local'].setdefault(partname, {'size': int(partinfo[2])})
        #if not disk['local'].has_key(partname):
            #disk['local'][partname] = {}
            #disk['local'][partname]['size'] = int(partinfo[2])

        if part_disk.has_key(partname):
            disk['local'][partname]['disk'] = part_disk.get(partname)

    return disk

def get_network_info():
    network = {}
    cmd = IFCONFIG_PATH
    #print exec_cmd(IFCONFIG_PATH)
    #return ifconfig_parser(output)

    ifcfg = ifconfig_parser(exec_cmd(IFCONFIG_PATH))
    for i in ifcfg:
        network[i.pop('name')] = i

    return network

def ifconfig_parser(output):
    output = output.strip().split('\n\n')
    ifs = []
    for i in output:    # process each interface
        interface = {}
        lines = i.splitlines()
        fl = lines[0].strip().split()
        interface['name'], interface['hwaddr'] = fl[0], fl[-1]

        for line in lines[1:]:
            m = re.search('(?<= MTU:)\d+(?= )', line)
            if m is not None:
                interface['mtu'] = m.group(0)
                break   # our processing stops at this line

            m = re.findall('[^|(?<= )]\w+ *\w+: ?[^ ]+', line.strip())
            for field in m:
                #print field.split(':', 1)
                k, v = field.split(':', 1)
                k = k.lower().replace(' ', '_')
                # sometimes a interface has multiple address
                # (only need one of them)
                if interface.has_key(k):   
                    continue
                v = v.strip().lower()
                interface[k] = v

        ifs.append(interface)
    return ifs

def get_os_info():
    issue = "issue:\n" + exec_cmd('cat /etc/issue')
    version = "version:\n" + exec_cmd('cat /proc/version')
    return issue + version

def get_uuid():
    import uuid
    return str(uuid.uuid1())[-12:]

def get_local_ip():
    ip = os.popen("/sbin/ifconfig | grep 'inet addr' | awk '{print $2}'").read()
    ip = ip[ip.find(':')+1 : ip.find('\n')]
    return ip

if __name__ == '__main__':
    #print 'CPU:\n', get_cpu_info()
    #print
    #print 'OS:\n', get_os_info()
    #print
    #print 'Memory:\n', get_mem_info()
    #print 
    #print 'Disk:\n', get_disk_info()
    #import pprint
    #pp = pprint.PrettyPrinter(indent=2)
    
    #pp.pprint(get_platform_info())
    #print get_network_info()
    print get_local_ip()
