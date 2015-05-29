
import struct

from snjdck import *

import Config


class LogicLinker(Linker):
	def handlePacket(self, packet):
		fileno = read_uint(packet)
		self.sendTo(Config.ID_GATE, packet[:4] + b"recv:" + packet[4:])


clientMgr = ClientManager()
clientMgr.regLinker(LogicLinker, Config.CENTER_IP, Config.CENTER_PORT, Config.ID_LOGIC)
clientMgr.run()