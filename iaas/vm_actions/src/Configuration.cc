/*
 * Configuration.cc
 *
 *  Created on: May 4, 2012
 *      Author: Wuxl
 */

#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include "Configuration.h"

Configuration::Configuration(const char * filename)
	:EQU("="),SPACE(" "),lf("\n"),cr("\r"),crlf("\r\n"),note("#"){

	valid  = read_conf(filename);

}

int Configuration::read_conf(const char * filename){
		char line[512];
		FILE * fp;

		char *s1;
		char *s2;

		fp = fopen(filename,"rb");
                if(fp == NULL)return -1;

		while(fgets(line,512,fp)){
			if(!strlen(line)||!strncmp(line,note,1)||!strcmp(line,cr)||!strcmp(line,crlf)||!strcmp(line,lf)){
				continue;
			}

			s1 = strtok(line,EQU);
			s2 = strtok(NULL,crlf);

			if(!s2){
				s2 = strtok(NULL,cr);
			}

			if(!s1||!s2){
				continue;
			}

			conf.insert(make_pair(s1,s2));
		}


		return 0;

}

int Configuration::conf_format(){

        if(valid==-1)return -1;

	DBHost = conf["DBHost"];

	DBPort		= atoi(conf["DBPort"].c_str());

	DBUsername	= conf["DBUsername"];

	DBPassword	= conf["DBPassword"];

	DBDatabase	= conf["DBDatabase"];

	ONEPort		= atoi(conf["ONEPort"].c_str());

	Log		= conf["Log"];

        return 0;
}




