/*
 * VirtualMachineSetDns.cc
 *
 *  Created on: May 2, 2012
 *      Author: Wuxl
 */
#include "AttachRequestManager.h"

AttachRequestManager::VirtualMachineSetDns::VirtualMachineSetDns(Attaches * _attaches){
	attaches = _attaches;
	_signature = "A:ss";
}

void AttachRequestManager::VirtualMachineSetDns::execute(
		xmlrpc_c::paramList const &paramList,
		xmlrpc_c::value * const retvalP){
	string vmid ;
	string dns;

	int 	rc;

	vector<xmlrpc_c::value>		arrayData;
	xmlrpc_c::value_array *		arrayResult;


	vmid = xmlrpc_c::value_string(paramList.getString(0));
	dns  = xmlrpc_c::value_string(paramList.getString(1));

	rc = attaches->set_dns(vmid,dns);

	if(rc == 0 ){
		arrayData.push_back(xmlrpc_c::value_boolean(true));
	}
	else{
		arrayData.push_back(xmlrpc_c::value_boolean(false));
	}

	arrayResult = new xmlrpc_c::value_array(arrayData);

	*retvalP = * arrayResult;

	delete arrayResult;

	return;


}




