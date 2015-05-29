
import socket

import Config

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((Config.IP_843, 843))
server.listen(5)

while True:
	client, address = server.accept()
	buff = client.recv(1024)
	print(address, buff)
	client.sendall(b'<cross-domain-policy><allow-access-from domain="*" to-ports="*" /></cross-domain-policy>')
	client.close()
	