/*
 * VirtualMachineSshPort.cc
 *
 *  Created on: Apr 23, 2012
 *      Author: Wuxl
 */


#include "AttachRequestManager.h"

AttachRequestManager::VirtualMachinePort::VirtualMachinePort(Attaches*	_attaches)
	:attaches(_attaches)
{
	_signature = "A:ss";

}

void AttachRequestManager::VirtualMachinePort::execute(
		xmlrpc_c::paramList const & paramList, xmlrpc_c::value * const retvalP)
{
	string	vid;
	string 	ip;
        string  inner_port;

	string port;

	int rc;

	vector<xmlrpc_c::value> arrayData;
	xmlrpc_c::value_array*	arrayResult;

	vid = xmlrpc_c::value_string(paramList.getString(0));
	ip  = xmlrpc_c::value_string(paramList.getString(1));
	inner_port = xmlrpc_c::value_string(paramList.getString(2));

	std::cout<<vid<<ip<<inner_port<<std::endl;
	rc = attaches->get(vid,ip,inner_port,port);

	if(rc == 0){
		arrayData.push_back(xmlrpc_c::value_boolean(true));
		arrayData.push_back(xmlrpc_c::value_string(port));
	}
	else{
		arrayData.push_back(xmlrpc_c::value_boolean(false));
	}

	arrayResult = new xmlrpc_c::value_array(arrayData);

	*retvalP = *arrayResult;

	delete arrayResult;

	return;
}

