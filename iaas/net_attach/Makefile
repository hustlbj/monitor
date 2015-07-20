VPATH = src

CFLAGS = -g -Iinclude

CLIBS =  -g -lpthread -L /usr/lib64/mysql -lmysqlclient -lxmlrpc_server_abyss++ -lxmlrpc_client++

OBJECTS = MySqlDB.o Attaches.o VirtualMachinePort.o VirtualMachineReleasePort.o VirtualMachineQueryPort.o \
		  VirtualMachineIpv6.o  VirtualMachineSetIpv6.o AttachRequestManager.o Feedback.o Log.o \
		  VirtualMachineDns.o VirtualMachineSetDns.o Configuration.o  main.o 

CC = g++

all : VmNetAttach

$(OBJECTS) : %.o : %.cc
	$(CC)  -g -c $^  $(CFLAGS)

VmNetAttach : $(OBJECTS)
	$(CC) -g -o $@ $^ $(CLIBS)
	
clean:
	rm -rf *.o VmNetAttach
	 

