/*
 * VirtualMachineQueryPort.cc
 *
 *  Created on: Apr 24, 2012
 *      Author: Wuxl
 */

#include "AttachRequestManager.h"

AttachRequestManager::VirtualMachineQueryPort::VirtualMachineQueryPort(Attaches* _attaches){
	attaches = _attaches;
	_signature = "A:s";
}

void AttachRequestManager::VirtualMachineQueryPort::execute(
		xmlrpc_c::paramList const & paramList, xmlrpc_c::value * const retvalP){

	string vid ;
	string port;
	string inner_port;

	vector<xmlrpc_c::value>		arrayData;
	xmlrpc_c::value_array *		arrayResult;

	vid = xmlrpc_c::value_string(paramList.getString(0));

	int rc = attaches->port(vid,port,inner_port);

	if(rc==0){
		arrayData.push_back(xmlrpc_c::value_boolean(true));
		arrayData.push_back(xmlrpc_c::value_string(port));
		arrayData.push_back(xmlrpc_c::value_string(inner_port));
	}else
	{
		arrayData.push_back(xmlrpc_c::value_boolean(false));
	}

	arrayResult = new xmlrpc_c::value_array(arrayData);

	*retvalP= * arrayResult;

	delete arrayResult;

	return;
}
