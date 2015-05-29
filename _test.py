
import socket
import struct

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("192.168.1.107", 7410))

while True:
	val = input("input:")
	valBytes = val.encode("utf8")
	head = struct.pack(">H", len(valBytes))
	sock.send(head+valBytes)
	recv = sock.recv(1024)
	if not recv:
		break
	print(recv)
