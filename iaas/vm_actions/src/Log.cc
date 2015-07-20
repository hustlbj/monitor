/*
 * Log.cc
 *
 *  Created on: Apr 26, 2012
 *      Author: Wuxl
 */

#include <time.h>

#include "Log.h"

#include <string.h>

Filelog::Filelog(const string & _filename){

	ofstream file;
	filename = strdup(_filename.c_str());
	file.open(filename,ios_base::app);

	if(file.fail()){

	}

	if(file.is_open()){
		file.close();
	}
}

void Filelog::log(const string & message){
	char buf[64];
	time_t log_time;

	ofstream file;

	log_time = time(0);
	ctime_r(&log_time,buf);
	buf[24]=0;

	file.open(filename,ios_base::app);

	if(file.is_open()){

		file<<"[ "<<buf<<" ]";
		file<<" "<<message;
		file<<"\n";
		file.flush();
		file.close();
	}

	return ;

}




