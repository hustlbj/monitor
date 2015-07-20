/*
 * XmlrpcServer.h
 *
 *  Created on: Jun 5, 2012
 *      Author: Wuxl
 */

#ifndef XMLRPCSERVER_H_
#define XMLRPCSERVER_H_

#include<xmlrpc-c/base.hpp>
#include<xmlrpc-c/registry.hpp>
#include<xmlrpc-c/server_abyss.hpp>

#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>

#include"Log.h"
#include"ActionManager.h"

class XmlrpcServer
{
public:
	XmlrpcServer(const string & logfile,
				unsigned port,
				ActionManager *am);

	~XmlrpcServer(){};

	void initDeamon();

	void set_up();

	void start();
private:
	xmlrpc_c::registry		_registry;
	xmlrpc_c::serverAbyss*	_abyssServer;

	unsigned				_port;
	FilelogTS *				_log;

	ActionManager *			_am;
};




#endif /* XMLRPCSERVER_H_ */
