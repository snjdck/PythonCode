
from snjdck import *

import Config
import MsgDef

class GateClient(Client):
	def onConnected(self):
		self.linker = self.getLinker(Config.ID_GATE)
		self.linker.sendMsg(Config.ID_LOGIC, self.fileno(), MsgDef.ID_CONNECT)

	def onClose(self):
		self.linker.sendMsg(Config.ID_LOGIC, self.fileno(), MsgDef.ID_DISCONNECT)
		super().onClose()

	def handlePacket(self, packet):
		self.linker.sendTo(Config.ID_LOGIC, self.fileno(), packet)

class GateLinker(Linker):
	def handlePacket(self, buffer):
		fileno = read_uint(buffer)
		#packet = Packet(buffer[4:])
		self.getClient(fileno).send(buffer[4:])


clientMgr = ClientManager()
clientMgr.regLinker(GateLinker, Config.ID_GATE)
clientMgr.regServer(Config.GATE_IP, Config.GATE_PORT, GateClient)
clientMgr.run()