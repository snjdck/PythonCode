
from snjdck import *

import Config

serviceDict = {}

class CenterServerClient(Client):
	def __init__(self, clientMgr, sock):
		super().__init__(clientMgr, sock)
		self.isNameSet = False

	def handlePacket(self, packet):
		if not self.isNameSet:
			serviceId = read_ushort(packet)
			serviceDict[serviceId] = self
			self.isNameSet = True
			self.serviceId = serviceId
			return

		for serviceId in serviceDict:
			if serviceId == self.serviceId:
				continue
			service = serviceDict[serviceId]
			service.send(packet)


clientMgr = ClientManager()
clientMgr.regServer(Config.CENTER_IP, Config.CENTER_PORT, CenterServerClient)
clientMgr.run()