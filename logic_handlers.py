
from handler_mgr import *
import MsgDef

clientCount = 0

@bindMsg(MsgDef.ID_CONNECT)
def _onConnect(self, fileno, packet):
	self.clientDict[fileno] = None
	print("client connect")
	global clientCount
	clientCount += 1
	if 2 == clientCount:
		msgData = {"first":True}
		for client_fileno in self.clientDict:
			self.sendTo(client_fileno, packet.encode(MsgDef.ID_BEGIN_CHESS, msgData))
			msgData["first"] = False

@bindMsg(MsgDef.ID_DISCONNECT)
def _onDisConnect(self, fileno, packet):
	del self.clientDict[fileno]
	print("client disconnect")
	global clientCount
	clientCount -= 1

@bindMsg(MsgDef.ID_CHAT)
def _onChat(self, fileno, packet):
	for client_fileno in self.clientDict:
		self.sendTo(client_fileno, packet.tobytes())

@bindMsg(MsgDef.ID_ACTION)
def _onAction(self, fileno, packet):
	for client_fileno in self.clientDict:
		if fileno == client_fileno:
			continue
		self.sendTo(client_fileno, packet.tobytes())