
from snjdck import *

import Config

class Server843Client(Client):
	def onRecv(self):
		sock, address = self.sock.accept()
		buff = sock.recv(1024)
		print(address, buff)
		sock.sendall(b'<cross-domain-policy><allow-access-from domain="*" to-ports="*" /></cross-domain-policy>')
		sock.close()


clientMgr = ClientManager()
clientMgr.regServer(Config.IP_843, 843, Server843Client)
clientMgr.run()
	