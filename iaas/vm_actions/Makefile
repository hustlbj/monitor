#DEBUG = y

VPATH = src

CFLAGS = -g -Iinclude

ifeq ($(DEBUG),y)
	DEBFLAGS = -DMQDEBUG
endif	

CFLAGS += $(DEBFLAGS)

CLIBS = -g  -lpthread -L /usr/lib64/mysql -lmysqlclient -lxmlrpc_server_abyss++ -lxmlrpc_client++ -lssl -lcrypto

OBJECTS = main.o Actions.o Log.o MySqlDB.o ActionManager.o XmlrpcServer.o ONEClient.o Configuration.o

CC = g++

all : VmActQueue

$(OBJECTS) : %.o : %.cc
	$(CC)  -c $^  $(CFLAGS)	

VmActQueue : $(OBJECTS)
	$(CC) -o $@ $^ $(CLIBS)
	
clean:
	rm -rf *.o VmActQueue
	 

