/*
 * VirtualMachineDns.cc
 *
 *  Created on: May 2, 2012
 *      Author: Wuxl
 */

#include "AttachRequestManager.h"

AttachRequestManager::VirtualMachineDns::VirtualMachineDns(Attaches * _attaches){
	attaches = _attaches;
	_signature = "A:s";
}

void AttachRequestManager::VirtualMachineDns::execute(
			xmlrpc_c::paramList const & paramList,
			xmlrpc_c::value * const retvalP){
	string vmid;

	string dns;

	int 	rc;

	vector<xmlrpc_c::value>			arrayData;
	xmlrpc_c::value_array	*		arrayResult;

	vmid = xmlrpc_c::value_string(paramList.getString(0));

	rc = attaches->vm_dns(vmid,dns);

	if(rc ==0){
		arrayData.push_back(xmlrpc_c::value_boolean(true));
		arrayData.push_back(xmlrpc_c::value_string(dns));
	}else
	{
		arrayData.push_back(xmlrpc_c::value_boolean(false));
	}

	arrayResult = new xmlrpc_c::value_array(arrayData);

	*retvalP = *arrayResult;

	delete arrayResult;

	return;

}




