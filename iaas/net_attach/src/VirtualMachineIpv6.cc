/*
 * VirtualMachineIpv6.cc
 *
 *  Created on: Apr 23, 2012
 *      Author: Wuxl
 */

#include "AttachRequestManager.h"

AttachRequestManager::VirtualMachineIpv6::VirtualMachineIpv6(Attaches* _attaches){
	attaches = _attaches;
	_signature ="A:s";
}

void AttachRequestManager::VirtualMachineIpv6::execute(
		 xmlrpc_c::paramList const &  paramList, xmlrpc_c::value * const retvalP)
{
	string ipv6;

	string vid;

	int rc;

	vector<xmlrpc_c::value>		arrayData;
	xmlrpc_c::value_array*		arrayResult;

	vid = xmlrpc_c::value_string(paramList.getString(0));


	rc = attaches->vm_ipv6(vid,ipv6);


	if(rc==0){
		arrayData.push_back(xmlrpc_c::value_boolean(true));
		arrayData.push_back(xmlrpc_c::value_string(ipv6));
	}
	else{
		arrayData.push_back(xmlrpc_c::value_boolean(false));
	}

	arrayResult = new xmlrpc_c::value_array(arrayData);

	*retvalP = *arrayResult;

	delete arrayResult;
	return;
}


