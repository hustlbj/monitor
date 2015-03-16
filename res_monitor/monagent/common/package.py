#!/usr/bin/env python
import zlib

class Package(object):
	"""
	Serializing and deserializing.
	"""

	# Seperator between sections
	SEP = '+'

	# End mark for package
	END = 'END'

	def __init__(self, type, message):
		super(Package, self).__init__()
		self.type = type
		self.message = message


	def serialize(self):
		"""
		Serializing
		"""

		msg_compresed = zlib.compress(self.message)
		return Package.SEP.join([self.type, msg_compresed, Package.END])

	@classmethod
	def deserialize(cls, spackage):
		"""
		Deserializing from string

		:returns: package object
		"""

		type, spackage = spackage.split(Package.SEP, 1)
		message = spackage.rsplit(Package.SEP, 1)[0]
		message  = zlib.decompress(message)
		return cls(type, message)


if __name__=="__main__":
	pack = Package('DATA', 'a'*300)

	data = pack.serialize()

	print data

	obj = Package.deserialize(data)
	print obj.type, obj.message
