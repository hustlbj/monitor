/*
 * AttachRequestManager.cc
 *
 *  Created on: Apr 24, 2012
 *      Author: Wuxl
 */

#include "AttachRequestManager.h"


void * arm_run_server(void *arg)
{
	AttachRequestManager * arm;

	if(arg == 0)
		return 0;

	arm = static_cast<AttachRequestManager*>(arg);

	arm->AbyssServer = new xmlrpc_c::serverAbyss(
				arm->ARMRegistry,
				arm->port,
				"tmp/attachRequestManager.log"
				);

	arm->AbyssServer->run();

	return 0;
}


AttachRequestManager::AttachRequestManager(Attaches * _attaches, unsigned int _port,const string _logfile)
{
	attaches	= _attaches;
	port		= _port;

	log			= new FilelogTS(_logfile);
}

void AttachRequestManager::register_xml_methods()
{
	xmlrpc_c::methodPtr vm_ipv6(
			new AttachRequestManager::VirtualMachineIpv6(attaches));

	xmlrpc_c::methodPtr vm_port(
			new AttachRequestManager::VirtualMachinePort(attaches));

	xmlrpc_c::methodPtr vm_dns(
				new AttachRequestManager::VirtualMachineDns(attaches));

	xmlrpc_c::methodPtr vm_set_ipv6(
			new AttachRequestManager::VirtualMachineSetIpv6(attaches));

	xmlrpc_c::methodPtr vm_release_port(
			new AttachRequestManager::VirtualMachineReleasePort(attaches));

	xmlrpc_c::methodPtr vm_query_port(
			new AttachRequestManager::VirtualMachineQueryPort(attaches));

	xmlrpc_c::methodPtr vm_set_dns(
			new AttachRequestManager::VirtualMachineSetDns(attaches));


	ARMRegistry.addMethod("vm.net.ipv6.info",vm_ipv6);
	ARMRegistry.addMethod("vm.net.ipv6.set",vm_set_ipv6);
	ARMRegistry.addMethod("vm.net.port.ask",vm_port);
	ARMRegistry.addMethod("vm.net.port.release",vm_release_port);
	ARMRegistry.addMethod("vm.net.port.query",vm_query_port);
	ARMRegistry.addMethod("vm.net.dns.info",vm_dns);
	ARMRegistry.addMethod("vm.net.dns.set",vm_set_dns);

	attaches->select(attaches->DB());
}

void AttachRequestManager::start(){
	register_xml_methods();

	init_daemon();

	AbyssServer = new xmlrpc_c::serverAbyss(
					ARMRegistry,
					port,
					"/tmp/attachRequestManager.log"
					);


	AbyssServer->run();

}

void AttachRequestManager::init_daemon(){
	pid_t pid, sid;

	string 			logpid;
	stringstream 	ss;

	pid = fork();
	if(pid<0){
		exit(EXIT_FAILURE);
	}

	if(pid > 0){
		exit(EXIT_SUCCESS);
	}

	sid = setsid();
	if(sid<0){
		exit(EXIT_FAILURE);
	}

	pid = fork();
	if(pid<0){
		exit(EXIT_FAILURE);
	}

	if(pid>0){
		exit(EXIT_SUCCESS);
	}

	close(STDIN_FILENO);
	close(STDOUT_FILENO);
	close(STDERR_FILENO);

	if(chdir("/home/crane")<0){
		exit(EXIT_FAILURE);
	}

	umask(0);

	pid = getpid();
	ss<<pid;
	ss>>logpid;

	log->log("PID: "+logpid+" -----------");
}

