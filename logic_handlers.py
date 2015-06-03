
from handler_mgr import *
import MsgDef

@bindMsg(MsgDef.ID_CONNECT)
def _onConnect(self, fileno, packet):
	self.clientDict[fileno] = None
	print("client connect")

@bindMsg(MsgDef.ID_DISCONNECT)
def _onDisConnect(self, fileno, packet):
	del self.clientDict[fileno]
	print("client disconnect")

@bindMsg(MsgDef.ID_CHAT)
def _onChat(self, fileno, packet):
	for client_fileno in self.clientDict:
		self.sendTo(client_fileno, packet.tobytes())