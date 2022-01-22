from backend.client.demo_parser import DemoParser
from backend.services import FinalDemoService
from backend.sauerconsts import gamemodes
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import shutil
import json

def parseTime(timestr):
	tsplit = timestr.split("T")
	year = int(tsplit[0].split("-")[0])
	month = int(tsplit[0].split("-")[1])
	day = int(tsplit[0].split("-")[2])
	hour = int(tsplit[1].split(":")[0])
	minute = int(tsplit[1].split(":")[1])
	second = int(tsplit[1].split(":")[2].split(".")[0])

	dtime = datetime(year, month, day, hour, minute, second)

	return int(round(dtime.timestamp()))

resp = requests.get("http://173.208.193.60:5000/info").text

soup = BeautifulSoup(resp)

parser = DemoParser()

for tr in soup.find_all("tr"):
	download_link = BeautifulSoup(str(tr)).find_all("td")
	try:
		soup = download_link[-1]
		download_link = str(BeautifulSoup(str(soup)).find("a").get("href"))
		download_url = f"http://173.208.193.60:5000{download_link}"
		gameid = download_link.replace("/download/", "").replace(".dmo", "")
		st_url = f"https://sauertracker.net/api/game/{gameid}"

		print(f"Game {gameid}")

		if FinalDemoService.already_exists(int(gameid)):
			print(f"Game {gameid} already added")
			continue

		info = json.loads(requests.get(st_url).text)
		demo = requests.get(download_url)
		with open("tmp.dmo", 'wb') as f:
			f.write(demo.content)

		demo_map, demo_mode, demo_players, _ = parser.parseDemo("tmp.dmo")

		if info["mapName"] != demo_map:
			print(f"{gameid}: map missmatch")
			continue

		if info["gameMode"] != gamemodes[demo_mode]:
			print(f"{gameid}: mode missmatch")
			continue

		exit = False

		players = info["players"]

		for player in players:
			if player["name"] not in demo_players:
				exit = True
				break

			if player["team"] != demo_players[player["name"]]["team"]:
				exit = True
				break

			if player["frags"] != demo_players[player["name"]]["frags"]:
				exit = True
				break

			if player["deaths"] != demo_players[player["name"]]["deaths"]:
				exit = True
				break

		if exit:
			print(f"{gameid}: player data missmatch")
			continue

		print(f"Adding game {gameid} to the database")
		shutil.move("tmp.dmo", f"demos/{gameid}.dmo")

		FinalDemoService.create(
                gameid=int(gameid),
                timestamp=parseTime(info["time"]),
                mapname=info["mapName"],
                gamemode=info["gameMode"],
                gametype=info["gameType"],
                host=info["host"],
                port=info["port"],
                demo_path=f"demos/{gameid}.dmo",
                serverdesc=info["description"]
            )

	except Exception as e:
		print(f"Error: {e}")
		pass
