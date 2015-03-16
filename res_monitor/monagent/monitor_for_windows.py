'''
use wmi to get windows system's info
use psutil to get monitored metrics
'''
import wmi
import os
import time
import psutil as ps

def get_platform_info_win(wmiService = None):
	host = {}
	host["components"] = {}
	if wmiService == None:
		wmiService = wmi.WMI()

	#os, only get the first one
	for sys in wmiService.Win32_OperatingSystem():
		host["components"]["os"] = "Version: " + str(sys.Caption.encode("UTF8")) \
			+ " " + str(sys.OSArchitecture.encode("UTF8")) \
			+ " Vernum: " + str(sys.BuildNumber)
		break

	#disk, get the logical disk partition
	disks = {}
	disks["local"] = {}
	'''
	for disk in wmiService.Win32_DiskDrive():
		device = str(disk.Caption)
		disks["local"][device] = {}
		disks["local"][device]["size"] = long(disk.Size)
	'''
	for disk in wmiService.Win32_LogicalDisk(DriveType = 3):
		part = str(disk.Caption)
		disks["local"][part] = {}
		disks["local"][part]["size"] = disk.Size
		disks["local"][part]["avail"] = disk.FreeSpace

	host["components"]["filesystem"] = disks

	#memory
	mem = {}
	cs = wmiService.Win32_ComputerSystem()
	mem["mem_total"] = int(cs[0].TotalPhysicalMemory)
	host["components"]["memory"] = mem

	#cpu, only get the first cpu
	cpus = {}
	cpus["cpu_num"] = 0
	for cpu in wmiService.Win32_Processor():
		cpus["cpu_num"] = cpu.NumberOfCores
		cpus["model_name"] = cpu.Name
		cpus["cpu_MHz"] = cpu.MaxClockSpeed 
		break
		
	host["components"]["cpu"] = cpus

	#network
	interfaces = []
	for net in wmiService.Win32_NetworkAdapterConfiguration(IPEnabled = 1):
		interface = {}
		interface["name"] = net.Description
		interface["ipaddr"] = net.IPAddress[0]
		interface["hwaddr"] = net.MACAddress
		interfaces.append(interface)
	host["components"]["network"] = interfaces

	return host

def get_process_status_win(proc_name, wmiService = None):
	if wmiService == None:
		wmiService = wmi.WMI()
	for process in wmiService.Win32_Process(name = proc_name):
		if process and process.ProcessId:
			return [True, process.ProcessId]
	return [False, -1]

def get_metrics_win():
	import psutil as ps
	metrics = {}
	#CPU
	cpu = ps.cpu_times()
	metrics["cpu_usage"] = ps.cpu_percent(interval = 1)
	metrics["cpu_user"] = cpu.user
	metrics["cpu_system"] = cpu.system
	metrics["cpu_idle"] = cpu.idle
	
	#MEM
	mem = ps.virtual_memory()
	metrics["mem_free"] = mem.free
	metrics["mem_used"] = mem.used
	metrics["mem_available"] = mem.available
	metrics["mem_usage"] = mem.percent
	swap = ps.swap_memory()
	metrics["swap_total"] = swap.total
	metrics["swap_used"] = swap.used
	metrics["swap_free"] = swap.free
	metrics["swap_usage"] = swap.percent 
	
	#DISK
	disk = ps.disk_io_counters(perdisk=True)
	for prefix in disk.keys():
		metrics[prefix + "-" + "read_count"] = disk[prefix].read_count
		metrics[prefix + "-" + "write_count"] = disk[prefix].write_count
		metrics[prefix + "-" + "read_bytes"] = disk[prefix].read_bytes
		metrics[prefix + "-" + "write_bytes"] = disk[prefix].write_bytes

	#NET
	net = ps.net_io_counters(pernic=True)
	for prefix in net.keys():
		metrics[prefix + "-" + "bytes_sent"] = net[prefix].bytes_sent
		metrics[prefix + "-" + "bytes_recv"] = net[prefix].bytes_recv
		metrics[prefix + "-" + "packets_sent"] = net[prefix].packets_sent
		metrics[prefix + "-" + "packets_recv"] = net[prefix].packets_recv

	return metrics

if __name__ == "__main__":
	wmiService = wmi.WMI()
	info = get_platform_info_win(wmiService)
	print info
	#print get_process_status_win("SublimeText.exe", wmiService)
	print get_metrics_win()
