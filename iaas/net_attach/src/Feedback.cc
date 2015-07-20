/*
 * Feedback.cc
 *
 *  Created on: Apr 25, 2012
 *      Author: Wuxl
 */

#include "Feedback.h"

Feedback::Feedback(unsigned int _port, const string & _ip){
	stringstream ss;
	ss<<"http://"<<_ip<<":"<<_port<<"/RPC2";
	url = ss.str();
	log = new FilelogTS("/tmp/arm.log");
}

/*
void Feedback::otter(const string & _method,const  string & ip,const  string &port){

	xmlrpc_c::value		   result;

	client.call(url,_method,"ss",&result,ip.c_str(),port.c_str());

	bool success = xmlrpc_c::value_boolean(result);

	if(success){
		log->log(_method+" Has Succeeded");
	}
	else{
		log->log(_method+" Has Failed");
	}

	return;
}*/

void Feedback::otter(const string & _method,const  string & ip,const  string &port, const string &innert_port){
	xmlrpc_c::value		   result;

	client.call(url,_method,"sss",&result,ip.c_str(),port.c_str(),innert_port.c_str());

	bool success = xmlrpc_c::value_boolean(result);

	if(success){
		log->log(_method+" Has Succeeded");
	}
	else{
		log->log(_method+" Has Failed");
	}

	return;	
}

void Feedback::configure_client(unsigned _port, const string & _ip){
	stringstream ss;
	ss<<"http://"<<_ip<<":"<<_port<<"/RPC2";
	url = ss.str();
}
