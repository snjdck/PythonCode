
import socket

def create_client(ip, port):
	sock = socket.socket()
	sock.connect((ip, port))
	return sock

def create_server(ip, port):
	sock = socket.socket()
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((ip, port))
	sock.listen(5)
	return sock