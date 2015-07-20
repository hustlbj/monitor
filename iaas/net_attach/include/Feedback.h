/*
 * Feedback.h
 *
 *  Created on: Apr 22, 2012
 *      Author: Wuxl
 */

#ifndef FEEDBACK_H_
#define FEEDBACK_H_

#include <map>
#include <string>
#include <vector>
#include <sstream>
#include <iostream>

#include <xmlrpc-c/base.hpp>
#include <xmlrpc-c/client_simple.hpp>

#include "Log.h"

using namespace std;

class Feedback{
public:
	Feedback(unsigned _port, const string& _ip );

	~Feedback(){
	};

	void configure_client(unsigned _port, const string & _ip);

	void unconfigure_client(){
		url = "";
	}

	void otter(const string& method,const string & ip,const string &port,const string &innert_port);
	/*void otter(const string& method,const string & ip,const  string &port);*/

private:
	xmlrpc_c::clientSimple client;

	FilelogTS * log;

	string					url;
};


#endif /* FEEDBACK_H_ */
