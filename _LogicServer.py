
from snjdck import *

import MsgDef
import Config

handlerDict = {}

def bindMsg(msgId):
	def wrapper(func):
		handlerDict[msgId] = func
		return func
	return wrapper

clientDict = {}

class LogicLinker(Linker):
	def handlePacket(self, buffer):
		fileno = read_uint(buffer)
		packet = Packet(buffer[4:])

		if packet.msgId not in handlerDict:
			print("packet.msgId not handled:", packet.msgId)
			return

		handler = handlerDict[packet.msgId]
		handler(self, fileno, packet)

	@bindMsg(MsgDef.ID_CONNECT)
	def _onConnect(self, fileno, packet):
		clientDict[fileno] = None
		print("client connect")

	@bindMsg(MsgDef.ID_DISCONNECT)
	def _onDisConnect(self, fileno, packet):
		del clientDict[fileno]
		print("client disconnect")

	@bindMsg(MsgDef.ID_CHAT)
	def _onChat(self, fileno, packet):
		for client_fileno in clientDict:
			self.sendTo(Config.ID_GATE, client_fileno, packet.tobytes())

clientMgr = ClientManager()
clientMgr.regLinker(LogicLinker, Config.ID_LOGIC)
clientMgr.run()