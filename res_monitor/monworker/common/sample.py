import socket
from package import Package

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(('', 11))

pack = Package('DATA', str(data))
server.send(pack.serialize())

server.close()



