
__all__ = ["ServerSocket", "ClientSocket"]

class Socket:
	def __init__(self, sock):
		sock.setblocking(False)
		self.sock = sock

	def fileno(self):
		return self.sock.fileno()

	def close(self):
		self.sock.close()


class ServerSocket(Socket):
	def onRecv(self, context):
		sock, address = self.sock.accept()
		self.onAccept(sock, context)

	def onAccept(self, sock, context):
		pass


from struct_ex import read_ushort, pack_ushort
headLen = 2

class ClientSocket(Socket):
	def __init__(self, sock):
		super().__init__(sock)
		self.recvBuff = bytes()
		self.sendBuff = bytes()
		self.isSending = False
		self.packetsRecv = []

	def onConnected(self):
		pass

	def _send(self, data, context):
		self.sendBuff += pack_ushort(headLen+len(data)) + data
		if not self.isSending:
			context.modifyWrite(self)
			self.isSending = True

	def onSend(self, context):
		bytesSend = self.sock.send(self.sendBuff)
		if bytesSend < len(self.sendBuff):
			self.sendBuff = self.sendBuff[bytesSend:]
		else:
			self.sendBuff = bytes()
			self.isSending = False
			context.modifyRead(self)

	def handlePackets(self):
		while len(self.packetsRecv) > 0:
			packet = self.packetsRecv.pop(0)
			self.handlePacket(packet)

	def handlePacket(self, packet):
		pass

	def onRecv(self, context):
		try:
			data = self.sock.recv(0x10000)
		except ConnectionResetError as e:
			self.onClose()
			return
		if not data:
			self.onClose()
			return

		self.recvBuff += data

		end = len(self.recvBuff)
		begin = 0

		while True:
			if end - begin < headLen:
				break
			packetLen = read_ushort(self.recvBuff, begin)
			if end - begin < packetLen:
				break;
			packet = self.recvBuff[begin+headLen:begin+packetLen]
			self.packetsRecv.append(packet)

			begin += packetLen

		if 0 < begin:
			if begin < end:
				self.recvBuff = self.recvBuff[begin:]
			else:
				self.recvBuff = bytes()

		self.handlePackets()

	def onClose(self):
		pass
