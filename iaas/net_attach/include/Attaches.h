/*
 * Attaches.h
 *
 *  Created on: Apr 22, 2012
 *      Author: Wuxl
 */

#ifndef ATTACHES_H_
#define ATTACHES_H_

#include <map>
#include <vector>
#include <sstream>
#include <string>

#include "ObjectSql.h"
#include "Feedback.h"
#include "Log.h"

#include <iostream>

using namespace std;

class Attach{
public:
	Attach(string _port, string _vid,string _inner_port,bool _used=true):
		port(_port),vid(_vid),inner_port(_inner_port),used(_used),ipv6("")
	{};

	Attach():
		port(""),vid(""),ipv6(""),dns(""),ip(""),inner_port("")
	{};

	~Attach(){};

	void set_ipv6(const string& _ipv6){
		ipv6 = _ipv6;
	}
	void set_dns(const string & _dns){
		dns = _dns;
	}
	void set_ip(const string & _ip){
		ip = _ip;
	}

	string get_port(){
		return port;
	}

	bool get_used(){
		return used;
	}

	string get_ipv6(){
		return ipv6;
	}

	string get_vid(){
		return vid;
	}

	string get_dns(){
		return dns;
	}

	string to_string(){
		string str = "vid:"+vid+" port:"+port+" ipv6:"+ipv6;
		return str;
	}

	string get_ip(){
		return ip;
	}

	string get_inner_port(){
		return inner_port;
	}

	int from_values( char ** values);


private:
	string			port;
	string		 	vid;
	string			ipv6;
	bool			used;
	string			dns;
	string 			ip;
	string 			inner_port;
};


class Attaches : public ObjectSql{
public:
	Attaches(SqlDB * _db, Feedback *_fd ,unsigned long _size,unsigned long _port_address):
		ObjectSql(),
		size(_size),n_used(0),current(0),db(_db),fd(_fd),port_address(_port_address)
	{
		log = new FilelogTS("/tmp/arm.log");
	};

	virtual ~Attaches(){

	}



	int get(const string &vid,const string &ip ,const string _inner_port,string & r_port);

	int release(const string vid);

	int set_ipv6(const string & vid,const string & _ipv6);

	int vm_ipv6(const string & vid, string &ipv6);

	int port(const string & vid, string &port, string &inner_port);

	int set_dns(const string & vid, const string & _dns);

	int vm_dns(const string & vid,  string & _dns);


	int select(SqlDB *db);

	SqlDB * DB(){
		return db;
	}
	/**
	 * Just for test
	 */
	void show_attaches(){
		map<string,Attach*>::iterator it;
		for(it = attaches.begin(); it != attaches.end(); it++){
			cout<<"vid:"<<it->second->to_string()<<endl;
		}
	}


private:

	string ipv6;

	SqlDB * db;

	Feedback * fd;

	unsigned int current;

	unsigned long size;

	int n_used;

	const char * table;

	unsigned long port_address;

	FilelogTS * log;


	/**
	 * vid , attach
	 */
	map<string, Attach *> attaches;

	bool check(string port);

	int add(string vid, string port, string ip, string inner_port);

	int del(string vid);

	int select_cb(void *nil, int num, char ** value, char ** names);

	int update(SqlDB *db);

	int insert(SqlDB *db);

	int drop(SqlDB *db);


};

#endif /* ATTACHES_H_ */
