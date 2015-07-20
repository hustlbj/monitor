/*
 * Configuration.h
 *
 *  Created on: May 4, 2012
 *      Author: Wuxl
 */

#ifndef CONFIGURATION_H_
#define CONFIGURATION_H_

#include <string>
#include <iostream>
#include <map>

using namespace std;

class Configuration{
public:
	Configuration(const char * filename);

	~Configuration(){};

	string	DBHost;

	int 	DBPort;

	string	DBUsername;

	string	DBPassword;

	string 	DBDatabase;

	int		FDPort;

	string	FDIp;

	int		RMPort;

	string	RMLog;

	int		StartPort;

	int 	PortsSize;

        int valid ;

	int conf_format();
private:
	int read_conf(const char * filename);


	map<string,string> conf;

	const char * EQU;

	const char * SPACE;

	const char * lf;

	const char * cr;

	const char * crlf;

	const char * note;
};


#endif /* CONFIGURATION_H_ */
