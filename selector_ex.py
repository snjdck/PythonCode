
import selectors

class Selector:
	def __init__(self, timeout=None):
		self.epoll = selectors.DefaultSelector()
		self.timeout = timeout

	def register(self, sock):
		self.epoll.register(sock, selectors.EVENT_READ)

	def unregister(self, sock):
		self.epoll.unregister(sock)

	def modifyRead(self, sock):
		self.epoll.modify(sock, selectors.EVENT_READ)

	def modifyWrite(self, sock):
		self.epoll.modify(sock, selectors.EVENT_READ | selectors.EVENT_WRITE)

	def close(self):
		self.epoll.close()

	def poll(self):
		events = self.epoll.select(self.timeout)
		for key, event in events:
			sock = key.fileobj
			if event & selectors.EVENT_READ:
				sock.onRecv(self)
			if event & selectors.EVENT_WRITE:
				sock.onSend(self)

	def run(self):
		try:
			while True:
				self.poll()
		finally:
			self.close()
