
from snjdck import *

import Config

class GateClient(Client):
	def handlePacket(self, packet):
		linker = self.getLinker(Config.ID_GATE)
		linker.sendTo(Config.ID_LOGIC, pack_uint(self.fileno()) + packet)

class GateLinker(Linker):
	def handlePacket(self, packet):
		fileno = read_uint(packet)
		self.getClient(fileno).send(packet[4:])


clientMgr = ClientManager()
clientMgr.regLinker(GateLinker, Config.ID_GATE)
clientMgr.regServer(Config.GATE_IP, Config.GATE_PORT, GateClient)
clientMgr.run()