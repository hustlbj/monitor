/*
 * ONEClient.h
 *
 *  Created on: Jun 5, 2012
 *      Author: Wuxl
 */

#ifndef ONECLIENT_H_
#define ONECLIENT_H_

#include<string>
#include<sstream>

#include<xmlrpc-c/base.hpp>
#include<xmlrpc-c/client_simple.hpp>

#include<openssl/sha.h>

#include"mq.h"
#include"Log.h"

using namespace std;

class ONEClient{
public:
	ONEClient(unsigned port, const string & ip, FilelogTS * log);

	~ONEClient(){};

	int do_action(const string & username,const string & action,const string &vmid);

private:
	string authorize(const string & username);

	xmlrpc_c::clientSimple client;

	string url;
	
	FilelogTS * _log;
};



#endif /* ONECLIENT_H_ */
