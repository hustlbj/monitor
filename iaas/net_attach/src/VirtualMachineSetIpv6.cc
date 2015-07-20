/*
 * VirtualMachineSetIpv6.cc
 *
 *  Created on: Apr 23, 2012
 *      Author: Wuxl
 */

#include "AttachRequestManager.h"

AttachRequestManager::VirtualMachineSetIpv6::VirtualMachineSetIpv6(Attaches* _attaches)
{
	attaches = _attaches;
	_signature = "b:ss";
}

void AttachRequestManager::VirtualMachineSetIpv6::execute(
		 xmlrpc_c::paramList const &  paramList,xmlrpc_c::value * const retvalP)
{
	string vid;
	string ipv6;

	int rc;

	xmlrpc_c::value_boolean *	boolResult;

	vid = xmlrpc_c::value_string(paramList.getString(0));
	ipv6 = xmlrpc_c::value_string(paramList.getString(1));

	rc = attaches->set_ipv6(vid,ipv6);

	if(rc ==0 ){
		boolResult = new xmlrpc_c::value_boolean(true);
	}else
	{
		boolResult = new xmlrpc_c::value_boolean(false);
	}

	*retvalP = * boolResult;

	delete boolResult;

	return;
}


