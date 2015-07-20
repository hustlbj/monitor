/*
 * AttachRequestManager.h
 *
 *  Created on: Apr 22, 2012
 *      Author: Wuxl
 */

#ifndef ATTACHREQUESTMANAGER_H_
#define ATTACHREQUESTMANAGER_H_

#include<xmlrpc-c/base.hpp>
#include<xmlrpc-c/registry.hpp>
#include<xmlrpc-c/server_abyss.hpp>
#include<vector>
#include<pthread.h>

#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>

#include "Attaches.h"
#include "MySqlDB.h"
#include "Feedback.h"
#include "Log.h"
#include <unistd.h>

using std::vector;

class AttachRequestManager{
public:
	AttachRequestManager(
		Attaches*		_attaches,
		unsigned		_port,
		const string	_logfile
	);

	~AttachRequestManager(){
	}

	void start();

private:
	xmlrpc_c::registry 		ARMRegistry;
	xmlrpc_c::serverAbyss	*AbyssServer;

	Attaches *				attaches;
	unsigned				port;

	FilelogTS * log;

	pthread_t				arm_server_thread;

	void register_xml_methods();

	friend void * arm_run_server(void * args);

	void init_daemon();

	class VirtualMachinePort : public xmlrpc_c::method
	{
	public:
		VirtualMachinePort(Attaches*	_attaches);
		virtual ~VirtualMachinePort(){};

		void execute(
				xmlrpc_c::paramList const & paramList,
				xmlrpc_c::value * const retvalP);
	
		/* data */
	private:
		Attaches * attaches;
	};

	class VirtualMachineReleasePort : public xmlrpc_c::method{
	public:
		VirtualMachineReleasePort(Attaches*	_attaches);

		virtual ~VirtualMachineReleasePort(){};

		void execute(
					xmlrpc_c::paramList const & paramList,
					xmlrpc_c::value * const retvalP);
	private:
		Attaches * attaches;

	};


	class VirtualMachineIpv6 : public xmlrpc_c::method{
	public:
		VirtualMachineIpv6(Attaches* _attaches);

		virtual ~VirtualMachineIpv6(){};

		void execute(
					xmlrpc_c::paramList const & paramList,
					xmlrpc_c::value * const retvalP);
	private:
		Attaches * attaches;
	};

	class VirtualMachineSetIpv6 : public xmlrpc_c::method{
	public:
		VirtualMachineSetIpv6(Attaches* _attaches);

		virtual ~VirtualMachineSetIpv6(){};

		void execute(
					xmlrpc_c::paramList const & paramList,
					xmlrpc_c::value * const retvalP);
	private:
		Attaches * attaches;
	};

	class VirtualMachineQueryPort : public xmlrpc_c::method{
	public:
		VirtualMachineQueryPort(Attaches* _attaches);

		virtual ~VirtualMachineQueryPort(){};

		void execute(
					xmlrpc_c::paramList const & paramList,
					xmlrpc_c::value * const retvalP);
	private:
		Attaches * attaches;
	};

	class VirtualMachineDns : public xmlrpc_c::method{
	public:
		VirtualMachineDns(Attaches * _attaches);

		virtual ~VirtualMachineDns(){};

		void execute(xmlrpc_c::paramList const & paramList,
					xmlrpc_c::value * const retvalp);
	private:
		Attaches * attaches;
	};

	class VirtualMachineSetDns : public xmlrpc_c::method{
	public:
		VirtualMachineSetDns(Attaches * _attaches);

		virtual ~ VirtualMachineSetDns(){};

		void execute(xmlrpc_c::paramList const & paramList,
					 xmlrpc_c::value * const retvalP);
	private:
		Attaches * attaches;
	};
};

#endif /* ATTACHREQUESTMANAGER_H_ */
