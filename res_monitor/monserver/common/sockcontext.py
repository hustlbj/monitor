#!/usr/bin/env python
import time
import select
import socket
import errno

from package import Package

class PollContext(object):
	"""
	Manage sockets using poll.
	"""

	READ = select.POLLIN | select.POLLPRI |select.POLLHUP | select.POLLERR
	WRITE = select.POLLOUT

	def __init__(self, sock_addr):
		super(PollContext, self).__init__()
		self.sock_addr = sock_addr

	def initialize(self):
		"""
		Initialize poller ,set up main socket and register it.
		"""

		# Create TCP socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setblocking(0)

		# Bind the socket to port
		self.sock.bind(self.sock_addr)

		# Listening for incoming connections
		print "Listening on %s:%s"%self.sock_addr
		self.sock.listen(1000)

		# Set up poller
		self.poller = select.poll()
		self.poller.register(self.sock, PollContext.READ)

		# initialize varible
		self.fd_set = {self.sock.fileno(): self.sock}
		self.messages = {} 


	def wait(self, timeout=1000):
		"""
		Wait for comming connection, or timeout	event.

		:param timeout: timeout,l default 1000 millisecond.
		:returns: list of events, each event is 3-element tuple.
		          first is event name, as one of TIMEOUT, REGISTER, DATA
		          second is data recieved from socket.
		          third is related socket object 
		"""

		results = []

		events = self.poller.poll(timeout)

		if len(events) == 0:
			return [("TIMEOUT", None, None)]

		for fd, flags in events:
			s = self.fd_set[fd]

			# Handle input event
			if flags & select.POLLIN:

				if s == self.sock:
					client, addr = s.accept()
					print "new connection from %s:%s\n" % client.getpeername()
					
					client.setblocking(0)
					self.poller.register(client, PollContext.READ)
					self.fd_set[client.fileno()] = client
					self.messages[client.fileno()] = ""
					
				else:

					data = s.recv(4096)

					if data:
						self.messages[s.fileno()] += data
						# If recieve all data of package
						if data.endswith(Package.END):

							packet = Package.deserialize(self.messages[s.fileno()])
							self.messages[s.fileno()] = ''

							results.append((packet.type, packet.message, s))

					else:
						print "closing socket"
						self.poller.unregister(s)
						
						del self.fd_set[s.fileno()]
						del self.messages[s.fileno()]

						s.close()

			# Handle hung-up event
			elif flags & select.POLLHUP:
				pass

			# Handle error evetn
			elif flags & select.POLLERR:
				pass

		return results


		

class SocketContext(object):
	"""
	Manage socket using long connection.
	"""

	def __init__(self, sock_addr):
		super(SocketContext, self).__init__()
		self.sock_addr = sock_addr
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def initialize(self):
		"""
		Initialize main socket.

		Connect to mon-server.
		"""

		try:
			self.sock.connect(self.sock_addr)
		except socket.error, e:
			if e.errno == errno.EISCONN:
				self.sock.close()
				self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			raise e



	def settimeout(self, timeout=1.0):
		"""
		Set timeout of main socket.

		:param timeout: timeout, float
		"""

		self.sock.settimeout(timeout)


	def wait(self):
		"""
		Wait for coming event or timout event.

		:returns: name of event, as TIMEOUT, DATA
		"""

		try:
			message = self.sock.recv(1024)
		except socket.timeout, e:
			return "TIMEOUT"
		except socket.error, e:
			print "an error occured"
			print e
			if e.errno == errno.EPIPE:
				return ''
		else:
			return message


	def send(self, data):
		"""
		Send to message to server.

		:param data: message to send.
		"""
		self.sock.send(data)

