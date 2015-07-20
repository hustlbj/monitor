/*
 * Attaches.cc
 *
 *  Created on: Apr 22, 2012
 *      Author: Wuxl
 */

#include "Attaches.h"

int Attach::from_values( char ** values){
	vid = values[1];
	port = values[2];
	ipv6 = values[3];
	inner_port = values[7];
        std::cout<<"vid:"<<vid<<"inner_port:"<<inner_port<<std::endl;
	if(values[5]!=NULL){
		dns = values[5];
	}

	if(values[6]!=NULL){
		ip = values[6];
	}

	if(values[4])
	{
		string str = values[4];

		if(str == "1")
			used = true;
		else
			used = false;
	}

	return 0;
}

int Attaches::select_cb(void *nil, int num, char ** values, char ** names){

	Attach *attach;

	if((!values[0])||(num!=8))
	{
		log->log("Read Database Wrong With Error Column");
                std::cout<<"ReadDatabase Wrong With Error Column"<<std::endl;
		return -1;
	}
        std::cout<<"Read Database over"<<std::endl;
	attach = new Attach();

	// construct attach
	attach->from_values(values);

	attaches.insert(make_pair(attach->get_vid(),attach));

	if(attach->get_used()){
		n_used++;
	}

	return 0;
}

int Attaches::select(SqlDB *db){
	int rc;
	stringstream ss;

	n_used = 0;

	set_callback(static_cast<Callbackable::Callback>(&Attaches::select_cb));

	ss<<"SELECT * FROM virtual_network_attach";


	rc = db->exec(ss,this);


	unset_callback();
	return rc;
}

int Attaches::insert(SqlDB *){
	return -1;
}

int Attaches::update(SqlDB *){
	return -1;
}

int Attaches::drop(SqlDB *){
	return -1;
}


int Attaches::get(const string& _vid,const string &_ip, const string _inner_port,string & r_port){

	map<string,Attach*>::iterator it;

	unsigned long	port;

	int				rc = -1;

	it = attaches.find(_vid);
	if(it!=attaches.end()){
		log->log("Port of VirtualMachine"+_vid+"exist");
		std::cout<<"Port of VirtualMachine"+_vid+"exist"<<std::endl;

		return -1;
	}
        std::cout<<"attaches get "<<std::endl; 
	for(unsigned int i=0;i<size;i++,current++){
		port = port_address + current%(size-2)+1;

		string str_port;

		stringstream ss;
		ss<<port;
		ss>>str_port;

		if(check(str_port)==false){
			stringstream	ss;
			string			str_port;

			ss<<port;
			ss>>str_port;

			log->log(str_port+" Allocated to VirtualMachine "+_vid);
			std::cout<<str_port+" Allocated to VirtualMachine "+_vid<<std::endl;

			rc = add(_vid,str_port,_ip,_inner_port);

			if(rc == 0)
			{
				log->log("vm.net.port.set"+_ip+" "+str_port+" start");
				std::cout<<"vm.net.port.set"+_ip+" "+str_port+" start"<<std::endl;
				fd->otter("vm.net.port.set",_ip,str_port,_inner_port);
				log->log("vm.net.port.set"+_ip+" "+str_port+" end");
				std::cout<<"vm.net.port.set"+_ip+" "+str_port+" end"<<std::endl;

				r_port = str_port;

				break;
			}

		}
	}


	return rc;
}

int Attaches::release(const string vid){
	return del(vid);
}


int Attaches::add(string vid, string port, string ip , string inner_port){



	Attach*			attach;
	int 			rc;
	stringstream 	cmd;

	string			ipv6;
	string			used = "0";




	attach = new Attach(port,vid,inner_port);
	attach->set_ip(ip);
	ipv6 = db->escape_str(attach->get_ipv6());
	if(attach->get_used())
		used = "1";

	cmd<<"INSERT INTO virtual_network_attach (vid,ssh_port,ipv6,used,dns,ip,inner_port) VALUES("
		<<	vid		<<","
		<<	port	<<",'"
		<<	ipv6	<<"',"
		<<	used	<<",'"
		<<	" "	<<"','"	
		<<	ip	<<"',"
		<<  inner_port  <<")";
        std::cout<<cmd.str()<<std::endl;

	rc = db->exec(cmd);
	if (rc == 0){

		log->log("Insert Virtual Machine "+vid+"With Port"+port+" Into Database");

		attaches.insert(make_pair(vid,attach));

		log->log("Insert Virtual Machine "+vid+"With Port"+port+" Into Attaches Map");

		n_used++;

		return 0;
	}
	return rc;
}

int Attaches::del(string vid){
	map<string,Attach*>::iterator it;

	stringstream ss;
	int rc;

	it = attaches.find(vid);

	if(it == attaches.end()){
		log->log("Virtual Machine "+vid+"Has No Port");

		return -1;
	}

	ss<<"DELETE FROM virtual_network_attach WHERE ssh_port ="<<it->second->get_port()<<" AND vid ="<<vid;

	rc = db->exec(ss);


	if(rc ==0){

		log->log("Delete Virtual Machine "+it->second->get_ip()+"From Database");

		n_used--;

		fd->otter("vm.net.port.release",it->second->get_ip(),it->second->get_port(),it->second->get_inner_port());

		delete it->second;

		attaches.erase(it);
	}
	else{

	}



	return 0;
}

bool Attaches::check(string port){
	map<string, Attach*>::iterator it;

	for(it = attaches.begin();it != attaches.end() ;it++){
		if(it->second->get_port() == port)
		{
			return true;
		}
	}

	return false;

}

int Attaches::vm_ipv6(const string & vid, string & ipv6)
{
	map<string , Attach*>::iterator it;

	it = attaches.find(vid);

	if(it != attaches.end()){
		ipv6 = it->second->get_ipv6();
		return 0;
	}

	return -1;
}

int Attaches::set_ipv6(const string & vid,const string & _ipv6){
	map<string , Attach*>::iterator it;

	int rc = -1;

	stringstream ss;

	it = attaches.find(vid);

	if(it == attaches.end()){
		log->log("Virtual Machine "+vid+" is not exits");
		return -1;
	}

	ss<<"UPDATE virtual_network_attach SET ipv6='"<<_ipv6<<"' WHERE vid ="<<vid;

	log->log(ss.str());

	rc = db->exec(ss,this);

	if(rc == 0){
		//it = attaches.find(vid);

		if(it!=attaches.end()){
			it->second->set_ipv6(_ipv6);
		}
		else{
			rc = -1;
		}

	}

	return rc;
}

int Attaches::port(const string& vid, string &port,string & inner_port){
	map<string , Attach*>::iterator it;

	it = attaches.find(vid);

	if(it!= attaches.end()){
		port = it->second->get_port();
                inner_port = it->second->get_inner_port();
		return 0;
	}

	return -1;
}

int Attaches::set_dns(const string & vid, const string & _dns){
	map<string,Attach*>::iterator it;

	int rc;

	stringstream ss;

	it = attaches.find(vid);

	if(it == attaches.end()){
		log->log("SET DNS - Virutal Machine "+vid+" Does Not Exist");
		return -1;
	}

	ss<<"UPDATE virtual_network_attach SET dns='"<<_dns<<"' WHERE vid ="<<vid;

	rc = db->exec(ss,this);

	if(rc == 0){
		it->second->set_dns(_dns);
		return 0;
	}


	return -1;
}

int Attaches::vm_dns(const string & vid,  string & _dns){
	map<string,Attach*>::iterator it;

	it = attaches.find(vid);

	if(it != attaches.end()){
		_dns = it->second->get_dns();
		return 0;
	}

	return -1;
}

