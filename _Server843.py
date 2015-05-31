
from snjdck import *

import Config

POLICY_FILE = b'<cross-domain-policy><allow-access-from domain="*" to-ports="*" /></cross-domain-policy>'

class Server843Client(Client):
	def onRecv(self, context):
		data = self.sock.recv(64)
		self.sock.sendall(POLICY_FILE)
		self.onClose()


clientMgr = ClientManager()
clientMgr.regServer(Config.IP_843, 843, Server843Client)
clientMgr.run()
