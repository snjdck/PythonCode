
from snjdck import *
import handler_mgr
import logic_handlers

import Config

class LogicLinker(Linker):
	def onConnected(self):
		super().onConnected()
		self.clientDict = {}

	def handlePacket(self, buffer):
		fileno = read_uint(buffer)
		packet = Packet(buffer[4:])
		handler_mgr.handleMsg(self, fileno, packet)

clientMgr = ClientManager()
clientMgr.regLinker(LogicLinker, Config.ID_LOGIC)
clientMgr.run()