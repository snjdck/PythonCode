
from selector_ex import *
from socket_factory import *
from struct_ex import *
from socket_ex import *

import Config

class ClientManager(Selector):
	def __init__(self):
		super().__init__(1.0)
		self.clientDict = {}
		self.linkerDict = {}

	def regLinker(self, factory, serviceId):
		linker = factory(self, serviceId)
		self.register(linker)
		linker.onConnected()
		self.linkerDict[serviceId] = linker

	def getLinker(self, serviceId):
		return self.linkerDict[serviceId]

	def regServer(self, ip, port, clientFactory):
		self.register(Server(ip, port, clientFactory))

	def addClient(self, client):
		self.clientDict[client.fileno()] = client
		self.register(client)

	def getClient(self, fileno):
		return self.clientDict[fileno]

	def removeClient(self, client):
		self.unregister(client)
		del self.clientDict[client.fileno()]


class Client(ClientSocket):
	def __init__(self, clientMgr, sock):
		self.clientMgr = clientMgr
		super().__init__(sock)

	def close(self):
		self.onClose()
		self.sock.close()

	def getClient(self, fileno):
		return self.clientMgr.getClient(fileno)

	def getLinker(self, serviceId):
		return self.clientMgr.getLinker(serviceId)

	def send(self, data):
		self._send(data, self.clientMgr)

	def sendTo(self, who, data):
		self.send(pack_uint(who) + data)

	def sendMsg(self, who, msgId, msgData=None):
		self.sendTo(who, Packet.encode(msgId, msgData))

	def onClose(self):
		self.clientMgr.removeClient(self)


class Server(ServerSocket):
	def __init__(self, ip, port, clientFactory):
		sock = create_server(ip, port)
		super().__init__(sock)
		self.clientFactory = clientFactory

	def onAccept(self, sock, context):
		client = self.clientFactory(context, sock)
		context.addClient(client)
		client.onConnected()


class Linker(Client):
	def __init__(self, clientMgr, serviceId):
		sock = create_client(Config.CENTER_IP, Config.CENTER_PORT)
		super().__init__(clientMgr, sock)
		self.serviceId = serviceId

	def onConnected(self):
		self.send(pack_ushort(self.serviceId))

	def onClose(self):
		self.clientMgr.unregister(self)


import json

class Packet:
	@staticmethod
	def encode(msgId, msgData):
		buffer = pack_ushort(msgId)
		if msgData:
			buffer += json.dumps(msgData, separators=(',',':')).encode()
		return buffer

	def __init__(self, buffer):
		self.msgId = read_ushort(buffer)
		self.msgData = None
		if len(buffer) > 2:
			self.msgData = json.loads(buffer[2:].decode())

	def tobytes(self):
		return Packet.encode(self.msgId, self.msgData)

