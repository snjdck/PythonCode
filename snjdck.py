
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
		linker = factory(self)
		self.register(linker)
		linker.send(pack_ushort(serviceId))
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
		client.close()


class Client(ClientSocket):
	def __init__(self, clientMgr, sock):
		super().__init__(sock)
		self.clientMgr = clientMgr

	def close(self):
		print("sock close")
		self.sock.close()
		self.sock = None
		self.recvBuff = None
		self.sendBuff = None

	def getClient(self, fileno):
		return self.clientMgr.getClient(fileno)

	def getLinker(self, serviceId):
		return self.clientMgr.getLinker(serviceId)

	def send(self, data):
		self._send(data, self.clientMgr)

	def sendTo(self, serviceId, data):
		self.send(pack_ushort(serviceId) + data)

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


class Linker(Client):
	def __init__(self, clientMgr):
		sock = create_client(Config.CENTER_IP, Config.CENTER_PORT)
		super().__init__(clientMgr, sock)

	def onClose(self):
		self.clientMgr.unregister(self)
