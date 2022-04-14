from backend.utils import getint, getstr, sauer2unicode
from dataclasses import dataclass
from backend.sauerconsts import *
import requests
import gzip
import json
import os
import io

@dataclass
class Stamp:
	Time: int
	Channel: int
	Length: int

@dataclass
class DemoHeader:
	Magic: bytes
	FileVersion: int
	ProtocolVersion: int

class DemoParser(object):
	def __init__(self):
		self.map = ""
		self.current_mode = 0
		self.frags = {}
		self.deaths = {}
		self.players = {}
		self.intermission = False

	def readStamp(self, stream):
		time = 0
		channel = 0
		length = 0
		error = None
		try:
			time = int.from_bytes(stream.read(4), byteorder='little')
			channel = int.from_bytes(stream.read(4), byteorder='little')
			length = int.from_bytes(stream.read(4), byteorder='little')
		except Exception as e:
			error = e

		return Stamp(time, channel, length), error

	def readPacket(self, stream):
		stamp, error = self.readStamp(stream)
		if error:
			return None, None, error

		buff = bytes([])

		try:
			buff = stream.read(stamp.Length)
		except Exception as e:
			return None, None, e

		return stamp, buff, None

	def readDemoHeader(self, stream):
		magic = b""
		fileversion = 0
		protocolversion = 0
		try:
			magic = stream.read(16)
			fileversion = int.from_bytes(stream.read(4), byteorder='little')
			protocolversion = int.from_bytes(stream.read(4), byteorder='little')
		except Exception as e:
			return None, e

		if magic.decode("utf-8") != "SAUERBRATEN_DEMO":
			return None, "reading demo header: wrong magic (not a demo file?)"

		header = DemoHeader(magic, fileversion, protocolversion)
		return header, None

	def parseWelcome(self, stamp, data, error):
		if error:
			print(f"error parsing demo: {error}")

		data = io.BytesIO(data)

		while data.tell() < data.getbuffer().nbytes:
			packet = getint(data)

			if packet == N_WELCOME:
				pass
			elif packet == N_MAPCHANGE:
				self.map = getstr(data)
				self.current_mode = getint(data)
				getint(data)

			elif packet == N_TIMEUP:
				getint(data)
			elif packet == N_CLIENT:
				getint(data)
				getint(data)
			elif packet == N_CURRENTMASTER:
				while getint(data) != -1:
					pass

			elif packet == N_SPECTATOR:
				for _ in range(3):
					getint(data)

			elif packet == N_SETTEAM:
				while getint(data) != -1:
					pass
				getint(data)

			elif packet == N_FORCEDEATH:
				for _ in range(2):
					getint(data)

			elif packet == N_TEAMINFO:
				getint(data)
			elif packet == N_RESUME:
				while getint(data) != -1:
					pass

			elif packet == N_INITAI:
				cn = getint(data)

				for _ in range(4): # Random bot variables
					getint(data)

				name = (getstr(data))
				team = (getstr(data))

				self.players[cn] = {
					"name": name,
					"team": team
				}


			elif packet == N_INITCLIENT:
				cn = getint(data)

				name = getstr(data)

				team = getstr(data)

				getint(data)

				self.players[cn] = {
					"name": name,
					"team": team
				}

			elif packet == N_INITFLAGS:
				getint(data)

			elif packet == N_BASESCORE:
				getint(data)
				getstr(data)
				getint(data)

			elif packet == N_BASES:
				bases = getint(data)
				for _ in range(bases*4):
					getint(data)

			elif packet == N_INITTOKENS:
				bases = getint(data)
				for _ in range(bases*4):
					getint(data)

			elif packet == N_CDIS:
				getint(data)

			elif packet == N_ITEMLIST:
				while getint(data) != -1:
					pass

			elif packet == N_PAUSEGAME:
				for _ in range(2):
					getint(data)

			elif packet == N_GAMESPEED:
				for _ in range(2):
					getint(data)

			elif packet == N_TEXT:
				getint(data)
				getstr(data)

			elif packet == 0:
				getint(data)
			else:
				# If we get to this point something definitely went wrong
				getint(data)

	def parseDemo(self, filename):
		try:
			self.map = ""
			self.current_mode = 0
			self.frags = {}
			self.deaths = {}
			self.players = {}
			self.intermission = False

			stream = gzip.open(filename, "rb")

			header, error = self.readDemoHeader(stream)

			if error:
				print(f"error parsing demo: {error}")
				return None, None, None, error

			if header.FileVersion != 1:
				print(f"error: unsupported file version (only version 1 is supported)")
				return None, None, None, "unsupported file version"

			stamp, data, error = self.readPacket(stream)
			self.parseWelcome(stamp, data, error)
			stamp, data, error = self.readPacket(stream)

			while not error and data:
				data = io.BytesIO(data)

				packet = getint(data)

				if packet == N_DIED:
					if not self.intermission:
						target = getint(data)
						actor = getint(data)

						if target not in self.deaths:
							self.deaths[target] = 0
						self.deaths[target] += 1

						if actor not in self.frags:
							self.frags[actor] = 0

						if target == actor or (self.players[target]["team"] == self.players[actor]["team"] and self.current_mode in teammodes):
							self.frags[actor] -= 1
						else:
							self.frags[actor] += 1

				elif packet == N_CLIENT:
					cn = getint(data)
					getint(data)

					nested_packet = getint(data)

					if nested_packet == N_SWITCHNAME:
						name = getstr(data)
						self.players[cn]["name"] = name

				elif packet == N_INITCLIENT:
					cn = getint(data)

					name = getstr(data)
					team = getstr(data)

					self.players[cn] = {
						"name": name,
						"team": team
					}

				elif packet == N_RESUME:
					cn = getint(data)
					state = getint(data)
					frags = getint(data)
					flags = getint(data)
					deaths = getint(data)

					self.frags[cn] = frags
					self.deaths[cn] = deaths

				elif packet == N_SETTEAM:
					cn = getint(data)
					team = getstr(data)
					self.players[cn]["team"] = team

				elif packet == N_INITAI:
					cn = getint(data)

					for _ in range(4): # Random bot variables
						getint(data)

					name = (getstr(data))
					team = (getstr(data))

					self.players[cn] = {
						"name": name,
						"team": team
					}

				elif packet == N_CDIS:
					cn = getint(data)
					if not self.intermission:
						self.players.pop(cn)

				elif packet == N_TIMEUP:
					seconds = getint(data)
					if seconds == 0:
						self.intermission = True

				stamp, data, error = self.readPacket(stream)

			result = []

			for player in self.players:
				frags = 0
				deaths = 0

				if player in self.frags:
					frags = self.frags[player]

				if player in self.deaths:
					deaths = self.deaths[player]

				result.append({
						"name": self.players[player]["name"],
						"team": self.players[player]["team"],
						"frags": frags,
						"deaths": deaths
					})

			return self.map, self.current_mode, result, None
		except Exception as e:
			return None, None, None, e
