
import struct

from snjdck import *

import Config

class GateClient(Client):
	def handlePacket(self, packet):
		linker = self.getLinker(Config.ID_GATE)
		linker.send(struct.pack(">HI", Config.ID_LOGIC, self.fileno()) + packet)

class GateLinker(Linker):
	def handlePacket(self, packet):
		fileno = read_uint(packet)
		self.getClient(fileno).send(packet[4:])


clientMgr = ClientManager()
clientMgr.regLinker(GateLinker, Config.CENTER_IP, Config.CENTER_PORT, Config.ID_GATE)
clientMgr.regServer(Config.GATE_IP, Config.GATE_PORT, GateClient)
clientMgr.run()