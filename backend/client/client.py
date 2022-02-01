from backend.utils import CanGetDemoFromServer, HashPassword, AnswerChallenge, getint, getstr, putint, randomstring
from backend.services import ServerPingService, SauerAuthKeyService, SauerPasswordService, DemolistCacheService
from ..sauerconsts import *
from pony import orm
import ctypes
import time
import enet
import io
import os

SERVER_PING_INTERVAL = 2
DEMO_SIZE_LOWER_BOUND = 280 # kB
DEMO_SIZE_UPPER_BOUND = 10 # MB

class DemosClient(object):
	def __init__(self):
		self.connected = False
		self.connecting = False
		self.received_demo_list = False
		self.host = enet.Host(None, 1, 3, 0, 0)
		self.peer = None
		self.current_ip = ""
		self.current_port = 0
		self.name = "demo_collector"
		self.queue = []
		self.getting_demo = False
		self.connected_at = 0
		self.cn = 0
		self.sessionid = 0

	@orm.db_session
	def ping_servers(self):
		servers = ServerPingService.servers()
		for server in servers:
			if self.connected or self.connecting:
				break

			if server.ignore:
				continue

			if len(server.games) <= 0:
				continue

			if (int(time.time()) - server.lastping) < SERVER_PING_INTERVAL:
				continue

			res = CanGetDemoFromServer(ip=server.host, port=server.port)
			server.lastping = int(time.time())

			if res != 0:
				continue

			for game in server.games:
				print(f"Connect game: {game}")

			self.connect(server.host, server.port)
			break
			

	def connect(self, ip, port):
		if self.peer:
			self.disconnect()

		self.peer = self.host.connect(enet.Address(ip.encode("utf-8"), port), 3)
		self.connecting = True
		self.current_ip = ip
		self.current_port = port

	def disconnect(self):
		if self.peer:
			self.peer.disconnect()
			self.peer = None

	@orm.db_session
	def disconnect_reset(self):
		self.connected = False
		self.connecting = False

		server_ping = ServerPingService.get_by_address(
			host=self.current_ip,
			port=self.current_port
		)

		for game in server_ping.games:
			game.server_ping = None

		self.current_ip = ""
		self.current_port = 0 
		self.received_demo_list = False
		self.queue = []
		self.getting_demo = False
		self.connected_at = 0
		self.cn = 0
		self.sessionid = 0


	def sendpacket(self, channel, packet, args):
		msg = bytes([packet])
		for arg in args:
			arg_type = type(arg)

			if arg_type == bytes:
				msg += arg
				continue

			if arg_type == int:
				msg += bytes([arg])
				continue

			if arg_type == str:
				if arg == "":
					msg += bytes([0])
					continue

				msg += bytes(arg.encode("utf-8"))
				continue

		packet = enet.Packet(msg)
		self.peer.send(channel, packet)

	def filter_index(self, index):
		return index > 0

	def auth(self, ip, port):
		if (authkey := SauerAuthKeyService.get_authkey(f"{ip} {port}")):
			self.sendpacket(1, N_AUTHTRY, [authkey.desc, b"\x00", authkey.name])

	def setmaster(self, ip, port):
		if (password := SauerPasswordService.get_password(f"{ip} {port}")):
			password_hash = HashPassword(self.cn, self.sessionid, password.password)
			self.sendpacket(1, N_SETMASTER, [self.cn, putint(b'', self.sessionid), password_hash])

	def parse_response(self, data):
		packet_type = getint(data)

		if packet_type == N_SERVINFO:
			print("N_SERVINFO")
			self.cn = getint(data)
			getint(data) # prot
			self.sessionid = getint(data)
			self.sendpacket(1, N_CONNECT, [self.name, 0, "", "", ""])

		if packet_type == N_WELCOME:
			print("N_WELCOME")
			self.connected = True
			self.connecting = False
			self.connected_at = int(time.time())
			self.auth(self.current_ip, self.current_port)
			self.setmaster(self.current_ip, self.current_port)
			self.sendpacket(1, N_LISTDEMOS, [])

		if packet_type == N_AUTHCHAL:
			print("N_AUTHCHAL")
			desc = getstr(data)
			id_ = getint(data)
			challenge = getstr(data)			
			authkey = SauerAuthKeyService.get_authkey(f"{self.current_ip} {self.current_port}")
			answer = ctypes.string_at(AnswerChallenge(challenge.encode("utf-8"), (authkey.key).encode("utf-8")))
			self.sendpacket(1, N_AUTHANS, [desc, b"\x00", putint(b'', id_), answer, b"\x00"])

		if packet_type == N_SERVMSG:
			print("N_SERVMSG")
			msg = getstr(data)
			if not self.received_demo_list:
				if "claimed auth" in msg or "claimed admin" in msg or "claimed master" in msg:
					self.sendpacket(1, N_LISTDEMOS, [])

		if packet_type == N_SENDDEMOLIST:
			print("N_SENDDEMOLIST")
			self.received_demo_list = True
			num = getint(data)
			for i in range(num):
				text = getstr(data)
				print(text)
				split = text.split(": ")[1].split(", ")
				mode, mapname, size = split[0], split[1], split[2]

				if "kB" in size:
					if float(size[:-2]) < DEMO_SIZE_LOWER_BOUND:
						continue

				if "MB" in size:
					if float(size[:-2]) > DEMO_SIZE_UPPER_BOUND:
						continue

				if DemolistCacheService.get_by_text(text):
					continue

				self.queue.append(i+1)

				DemolistCacheService.create(text)

			print(f"Queue: {self.queue}")

		if packet_type == N_SENDDEMO:
			print("N_SENDDEMO")
			getint(data)

			curpath = os.path.abspath(os.curdir)
			hash_name = randomstring()
			path = f"demos/temp/{hash_name}.dmo"
			print(f"Received demo {path}")
			f = open(path, "wb")
			demo = data.read()
			f.write(demo)
			f.close()

			self.getting_demo = False

		if packet_type == N_MAPCHANGE:
			print("N_MAPCHANGE")
			# Hopefully this works
			for i, _ in enumerate(self.queue):
				self.queue[i] -= 1

			self.queue = list(filter(self.filter_index, self.queue))

	def poll_demos(self):
		if self.getting_demo:
			return

		if not self.queue:
			return

		if not self.received_demo_list:
			return

		self.sendpacket(1, N_GETDEMO, [self.queue[0], 1])

		self.queue.pop(0)

		self.getting_demo = True


	def poll_events(self):
		event = self.host.service(0)
		if event.type == enet.EVENT_TYPE_CONNECT:
			print(f"Connected to {event.peer.address}")

		elif event.type == enet.EVENT_TYPE_DISCONNECT:
			print(f"Disconnected from {event.peer.address}")
			self.disconnect_reset()

		elif event.type == enet.EVENT_TYPE_RECEIVE:
			self.parse_response(io.BytesIO(event.packet.data))

	def check_disconnects(self):
		# In case we get stuck force disconnect after 1 minute
		if self.connected and (int(time.time()) - self.connected_at) > 60:
			self.disconnect()

		# Disconnect if we don't get demo list within first 20 seconds
		if not self.received_demo_list and self.connected and (int(time.time()) - self.connected_at) > 20:
			self.disconnect()

		# Got our demos so we can leave now
		if self.connected and not self.getting_demo and self.received_demo_list and len(self.queue) < 1:
			self.disconnect()

	def update(self):
		try:
			self.ping_servers()
			self.poll_events()
			self.poll_demos()
			self.check_disconnects()
		except Exception as e:
			print(f"Ran into an exception {e}")
			self.disconnect()


	def run(self):
		while True:
			self.update()
			time.sleep(0.02)
