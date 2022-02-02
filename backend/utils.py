from .services import SauerAuthKeyService, SauerPasswordService
from .tiger import tiger_hash
from .sauerconsts import *
import ctypes
import socket
import select
import string
import random
import io

auth = ctypes.cdll.LoadLibrary('./backend/auth.so') # Compiled with go build -buildmode=c-shared -o auth.so auth.go
AnswerChallenge = auth.Solve
AnswerChallenge.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
AnswerChallenge.restype = ctypes.c_void_p

def HashPassword(cn, sessionid, password):
	message = f"{cn} {sessionid} {password}"
	res = tiger_hash(message)
	password_hash = ""
	for i in range(3):
		password_hash += hex(res[i])[2:][::-1]

	return password_hash

def CanGetDemoFromServer(ip="", port=0):
	UDP_IP = ip
	UDP_PORT = port

	MESSAGE = b''
	MESSAGE = putint(MESSAGE, 100)
	MESSAGE = putint(MESSAGE, 100)
	MESSAGE = putint(MESSAGE, 100)

	pingsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	pingsock.sendto(MESSAGE, (UDP_IP, UDP_PORT+1))

	data = bytes()
	ready = select.select([pingsock], [], [], 0.5)
	if ready[0]:
		data = pingsock.recv(1024)

	data = io.BytesIO(data)

	# don't care about that
	for i in range(3):
		getint(data)

	players = getint(data)
	numofargs = getint(data)
	protocol = getint(data)
	mode = getint(data)
	timeleft = getint(data)
	maxclients = getint(data)
	mastermode = getuint(data)

	if PROTOCOL != protocol:
		return 1

	if players >= maxclients:
		return 1

	# Make sure we don't connect during an intermission
	if timeleft <= 10:
		return 1

	if mastermode not in [MM_AUTH, MM_OPEN, MM_VETO]:
		if not SauerAuthKeyService.get_authkey(f"{ip} {port}") and not SauerPasswordService.get_password(f"{ip} {port}"):
			return 1

	return 0

def sauer2unicode(arg):
	result = ""
	for i in arg:
		if type(i) == int:
			result += unicode_characters[i]
		else:
			result += unicode_characters[int.from_bytes(i, byteorder='little')]

	return result

def getuint(stream):
	# Should work for values up to 268435456
	n = int.from_bytes(stream.read(1), byteorder='little')
	if n == (1<<7):
		n += ((int.from_bytes(stream.read(1), byteorder='little')) << 7) - (1<<7)
		if n == (1<<14):
			n += ((int.from_bytes(stream.read(1), byteorder='little')) << 14) - (1<<14)
		if n == (1<<21):
			n += ((int.from_bytes(stream.read(1), byteorder='little')) << 21) - (1<<21)
	return n

def getint(stream):
	c = int.from_bytes(stream.read(1), byteorder='little', signed=True)
	if c == -128:
		n = int.from_bytes(stream.read(1), byteorder='little')
		n |= (int.from_bytes(stream.read(1), byteorder='little', signed=True))<<8
		return n
	elif c == -127:
		n = int.from_bytes(stream.read(1), byteorder='little')
		n |= (int.from_bytes(stream.read(1), byteorder='little'))<<8
		n |= (int.from_bytes(stream.read(1), byteorder='little'))<<16
		n |= (int.from_bytes(stream.read(1), byteorder='little'))<<24
		return n
	else:
		return c

def getstr(stream):
	buf = []
	val = int.from_bytes(stream.read(1), byteorder='little')
	while val != 0:
		buf.append(val)
		val = int.from_bytes(stream.read(1), byteorder='little')

	return sauer2unicode(buf)

def putint(buff, n):
	if n < 128 and n > -127:
		buff += n.to_bytes(1, byteorder='little', signed=True)
	elif(n < 0x8000 and n >= -0x8000):
		buff += (0x80).to_bytes(1, byteorder='little', signed=False)
		buff += n.to_bytes(2, byteorder='little', signed=True)
	else:
		buff += (0x81).to_bytes(1, byteorder='little', signed=False)
		buff += n.to_bytes(4, byteorder='little', signed=True)

	return buff

def uchar_to_char(n):
	if n in range(0, 256):
		if n > 127:
			return n - 256
		return n
	raise ValueError("uchar can take values between 0 and 255")

def char_to_uchar(n):
	if n in range(-128, 128):
		if n < 0:
			return n + 256
		return n
	raise ValueError("char can take values between -128 and 127")

def randomstring():
	return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=10))

