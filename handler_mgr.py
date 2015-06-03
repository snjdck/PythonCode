
__all__ = ["bindMsg", "handleMsg"]

_handlerDict = {}

def bindMsg(msgId):
	def wrapper(func):
		_handlerDict[msgId] = func
		return func
	return wrapper

def handleMsg(context, fileno, packet):
	if packet.msgId not in _handlerDict:
		print("packet.msgId not handled:", packet.msgId)
		return
	handler = _handlerDict[packet.msgId]
	handler(context, fileno, packet)