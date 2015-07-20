/*
 * ONEClient.cc
 *
 *  Created on: Jun 5, 2012
 *      Author: Wuxl
 */

#include"ONEClient.h"


ONEClient::ONEClient(unsigned int port, const string & ip, FilelogTS * log)
{
	stringstream ss;
	ss<<"http://"<<ip<<":"<<port<<"/RPC2";
	url = ss.str();
	_log = log;
}

string ONEClient::authorize(const string & username)
{
    SHA_CTX s;
    stringstream ss;

    unsigned char sha_result[20];
    char author[40];

    ss<<username<<"pass";

    SHA1_Init(&s);
    SHA1_Update(&s,ss.str().c_str(),ss.str().size());
    SHA1_Final(sha_result,&s);

    for(int i =0 ;i != 20; i++)
    {
            sprintf(author+i*2,"%.2x",sha_result[i]);
    }

    ss.str("");
    ss<<username<<":"<<author;
    return ss.str();

}

int ONEClient::do_action(const string & username,const string & action,const string &vmid)
{
	int rc = 0;
	bool success;
	string message;
	xmlrpc_c::value	result;

	string author = authorize(username.c_str());

#ifdef MQDEBUG
	PDEBUG("[ONEClient] test authorzie is %s\n",author.c_str());
#endif

	client.call(url,
				"one.vm.action",
				"ssi",
				&result,
				author.c_str(),
				action.c_str(),
				atoi(vmid.c_str()));

	vector<xmlrpc_c::value> values = xmlrpc_c::value_array(result).vectorValueValue();
	success = xmlrpc_c::value_boolean(values[0]);
	if(!success){
		message = xmlrpc_c::value_string(values[1]);

#ifdef MQDEBUG
		PDEBUG("[ONEClient] message is %s\n",message.c_str());
#else
		_log->log("[ONEClient] "+message);
#endif


		rc = -1;
	}

	return rc;
}
