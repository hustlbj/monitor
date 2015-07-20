/*
 * main.cc
 *
 *  Created on: Apr 21, 2012
 *      Author: Wuxl
 */

#include <string>

#include "vna.h"



using namespace std;

int main(int argc,char **argv){
	string file;
	char opt;

	if(argc == 1)
	{
		cerr<<"usage:"<<argv[0]<<" -f [filename] \n";
		exit(-1);
	}

	while((opt = getopt(argc,argv,"f:"))!=-1)
	{
		switch(opt){
			case 'f':
				file = optarg;
				break;
			default:
				cerr<<"usage:"<<argv[0]<<" -f [filename] \n";
				exit(-1);
				break;
		}
	};
	Configuration *conf = new Configuration(file.c_str());
        if(conf->conf_format() !=0){
		cerr<<"invalid filename"<<endl; 
		cerr<<"usage:"<<argv[0]<<" -f [filename] \n";
		exit(-1);
        }

	SqlDB * db  = new MySqlDB(conf->DBHost,conf->DBPort,conf->DBUsername,conf->DBPassword,conf->DBDatabase);

	Feedback * fd = new Feedback(conf->FDPort,conf->FDIp);

	Attaches * attaches = new Attaches(db,fd,conf->PortsSize,conf->StartPort);

	AttachRequestManager * arm = new AttachRequestManager(attaches,conf->RMPort,conf->RMLog);

	arm->start();

	return 0;
}


