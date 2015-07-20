/*
 * main.cc
 *
 *  Created on: Jun 4, 2012
 *      Author: Wuxl
 */
#include"ActionManager.h"
#include"MySqlDB.h"
#include"XmlrpcServer.h"
#include"Configuration.h"

#include<unistd.h>
#include<fcntl.h>
#include<sys/types.h>
#include<sys/stat.h>

#include<iostream>


using namespace std;

int main(int argc, char **argv){
	int				port	= 2649;
	time_t			timer	= 5;
	unsigned int	limit	= 3;
	string		file;

	MySqlDB *db;
	ActionManager *am;
	XmlrpcServer *server;
	Configuration * conf;


	char opt;
        if(argc == 1){
	     cerr<<"usage:"<<argv[0]<<" t [timer]"<<" p [port]"<<" l [limit]"<<" f [filename]"<<endl;
             exit(-1);
        }

	while((opt = getopt(argc,argv,"t:p:l:f:"))!=-1)
	{
		switch(opt){
			case 't':
				timer	= atoi(optarg);
				break;
			case 'p':
				port	= atoi(optarg);
				break;
			case 'l':
				limit	= atoi(optarg);
				break;
			case 'f':
				file = optarg;
				break;
			default:
				cerr<<"usage:"<<argv[0]<<" t [timer]"<<" p [port]"<<" l [limit]"<<" f [filename]"<<endl;
				exit(-1);
				break;
		}
	};



	#ifdef MQDEBUG
		PDEBUG("file name is %s\n",file.c_str());
	#endif	

	conf = new Configuration(file.c_str());
        
        if(conf->conf_format()==-1){
		cerr<<"Invalid Configuration !"<<endl;
		cerr<<"usage:"<<argv[0]<<" t [timer]"<<" p [port]"<<" l [limit]"<<" f [filename]"<<endl;
		exit(-1);
        }
	if(conf->Log==""){
		printf("log is emptry\n");
		return 1;
	}

        

	db = new MySqlDB(conf->DBHost,
					 conf->DBPort,
					 conf->DBUsername,
					 conf->DBPassword,
					 conf->DBDatabase,
					 conf->Log);

	am = new ActionManager(db,limit,timer,conf->Log);

	server = new XmlrpcServer(conf->Log,port,am);

	#ifndef	MQDEBUG
	server->initDeamon();
	#endif

	server->set_up();

	server->start();

	delete db;
	delete am;
	delete server;

	return 0;
}



