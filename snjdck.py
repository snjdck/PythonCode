
import socket
import selectors
import struct

def read_ushort(buffer, offset=0):
	return struct.unpack_from(">H", buffer, offset)[0]

def read_uint(buffer, offset=0):
	return struct.unpack_from(">I", buffer, offset)[0]

class ClientManager:
	def __init__(self):
		self.epoll = selectors.DefaultSelector()
		self.sockDict = {}
		self.clientDict = {}
		self.linkerDict = {}

	def regLinker(self, factory, ip, port, serviceId):
		linker = factory(self, ip, port)
		linker.serviceId = serviceId
		self.linkerDict[serviceId] = linker
		linker.tryConnect()

	def getLinker(self, serviceId):
		return self.linkerDict[serviceId]

	def regServer(self, ip, port, clientFactory):
		self.register(Server(self, ip, port, clientFactory))

	def register(self, sock):
		self.sockDict[sock.fileno()] = sock
		self.epoll.register(sock, selectors.EVENT_READ)

	def unregister(self, sock):
		self.epoll.unregister(sock)
		del self.sockDict[sock.fileno()]

	def modify(self, client, event):
		self.epoll.modify(client, event)

	def getClient(self, fileno):
		return self.clientDict[fileno]

	def addClient(self, client):
		self.clientDict[client.fileno()] = client
		self.register(client)

	def onClientClose(self, client):
		self.unregister(client)
		del self.clientDict[client.fileno()]
		client.close()

	def poll(self):
		events = self.epoll.select(1.0)
		for key, event in events:
			sock = key.fileobj
			if event & selectors.EVENT_READ:
				sock.onRecv()
			if event & selectors.EVENT_WRITE:
				sock.onSend()

	def run(self):
		try:
			while True:
				self.poll()
				self.update()
		finally:
			self.epoll.close()

	def update(self):
		for serviceId, linker in self.linkerDict.items():
			linker.onUpdate()


class Client:
	def __init__(self, clientMgr, sock):
		self.clientMgr = clientMgr
		self.sock = sock
		self.recvBuff = b""
		self.sendBuff = b""
		self.isSending = False
		self.recvPacketList = []

	def fileno(self):
		return self.sock.fileno()

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

	def handlePackets(self):
		while len(self.recvPacketList) > 0:
			packet = self.recvPacketList.pop()
			self.handlePacket(packet)

	def handlePacket(self, packet):
		pass
		#for fileno, client in self.clientMgr.clientDict.items():
		#	client.send(packet)

	def send(self, data):
		self.sendBuff += struct.pack(">H", len(data)) + data
		if not self.isSending:
			self.clientMgr.modify(self, selectors.EVENT_READ | selectors.EVENT_WRITE)
			self.isSending = True

	def sendTo(self, serviceId, data):
		self.send(struct.pack(">H", serviceId) + data)

	def onRecv(self):
		try:
			data = self.sock.recv(1024)
		except ConnectionResetError as e:
			self.onClose()
			return
		if not data:
			self.onClose()
			return
		
		self.recvBuff += data

		while True:
			if len(self.recvBuff) < 2:
				break
			bodyLen = struct.unpack_from(">H", self.recvBuff)[0]
			if len(self.recvBuff) < bodyLen + 2:
				break;
			packet = self.recvBuff[2:2+bodyLen]
			self.recvPacketList.append(packet)

			self.recvBuff = self.recvBuff[2+bodyLen:]

		self.handlePackets()

	def onSend(self):
		bytesSend = self.sock.send(self.sendBuff)
		if bytesSend < len(self.sendBuff):
			self.sendBuff = self.sendBuff[bytesSend:]
		else:
			self.sendBuff = b""
			self.clientMgr.modify(self, selectors.EVENT_READ)
			self.isSending = False

	def onClose(self):
		self.clientMgr.onClientClose(self)


class Server:
	def __init__(self, clientMgr, ip, port, clientFactory):
		self.clientFactory = clientFactory
		self.clientMgr = clientMgr
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((ip, port))
		sock.listen(5)
		sock.setblocking(False)
		self.sock = sock

	def fileno(self):
		return self.sock.fileno()

	def close(self):
		self.sock.close()

	def onRecv(self):
		sock, address = self.sock.accept()
		sock.setblocking(False)

		client = self.clientFactory(self.clientMgr, sock)
		self.clientMgr.addClient(client)


class Linker(Client):
	def __init__(self, clientMgr, ip, port):
		self.host = (ip, port)
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		Client.__init__(self, clientMgr, sock)

	def tryConnect(self):
		print("try to connnect")
		self.isConnected = self.sock.connect_ex(self.host) == 0
		if self.isConnected:
			self.sock.setblocking(False)
			self.regSelf()
			print("try ok")

	def regSelf(self):
		self.clientMgr.register(self)
		self.send(struct.pack(">H", self.serviceId))

	def onUpdate(self):
		if not self.isConnected:
			self.tryConnect()

	def onClose(self):
		self.clientMgr.unregister(client)
