/*
 * VirtualMachineReleaseSshPort.cc
 *
 *  Created on: Apr 23, 2012
 *      Author: Wuxl
 */

#include "AttachRequestManager.h"


AttachRequestManager::VirtualMachineReleasePort::VirtualMachineReleasePort(Attaches *_attaches){
	attaches = _attaches;
	_signature = "b:s";
}

void AttachRequestManager::VirtualMachineReleasePort::execute(
		 xmlrpc_c::paramList const & paramList, xmlrpc_c::value *  const retvalP)
{
	string vid;

	int rc;

	xmlrpc_c::value_boolean*	arrayResult;

	vid = xmlrpc_c::value_string(paramList.getString(0));

	rc = attaches->release(vid);

	if(rc == 0 ){
		arrayResult =  new xmlrpc_c::value_boolean(true);
	}
	else
	{
		arrayResult = new xmlrpc_c::value_boolean(false);
	}

	*retvalP = *arrayResult;
	delete arrayResult;
	return;
}

