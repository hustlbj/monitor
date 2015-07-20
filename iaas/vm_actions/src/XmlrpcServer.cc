/*
 * XmlrpcServer.cc
 *
 *  Created on: Jun 5, 2012
 *      Author: Wuxl
 */

#include"XmlrpcServer.h"


XmlrpcServer::XmlrpcServer(
		const string & logfile,
		unsigned int port,
		ActionManager *am)
{
	_log	= new FilelogTS(logfile);
	_port	= port;
	_am		= am;
	_log->log("create log");
}

void XmlrpcServer::initDeamon()
{
	_log->log("initDeamon Start");
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

	_log->log("PID: ------"+logpid+" -----------");
}

void XmlrpcServer::start()
{
	_abyssServer = new xmlrpc_c::serverAbyss(
						_registry,
						_port,
						"/tmp/xmlrpcserver.log"
						);

#ifdef MQDEBUG
	PDEBUG("[XmlrpcServer] abyssServer run\n");
#else
	_log->log("[XmlrpcServer] abyssServer run");
#endif

	_abyssServer->run();

	_am->wait();
}

void XmlrpcServer::set_up()
{
	xmlrpc_c::methodPtr vm_action(_am);

	_registry.addMethod("vm.action.mq",vm_action);

#ifdef MQDEBUG
	PDEBUG("[XmlrpcServer] Scheduler Thread create\n");
#else
	_log->log("[XmlrpcServer] Scheduler Thread creat");
#endif

	_am->start();
}
