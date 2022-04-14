from backend.services import SauertrackerAPI, SauertrackerGameService, SauertrackerGameInfoService, UnprocessedDemoFileInfoService, FinalDemoService
from apscheduler.schedulers.background import BackgroundScheduler
from backend.client.demo_parser import DemoParser
from backend.utils import getcurtime
from backend.sauerconsts import *
from pony import orm
import shutil
import time
import glob
import json
import ast
import os

def check_for_new_games():
    games = SauertrackerAPI.games(timeout=30, limit=30)

    if not games:
        return

    for game in games:
        if game["gametype"] not in ["duel", "mix", "clanwar", "intern"]:
            continue

        if SauertrackerGameService.already_added(game["id"]):
            continue

        print(f"[{getcurtime()}] Added game {game['id']} to the database")

        SauertrackerGameService.create(
            gameid = game["id"],
            mapname = game["map"],
            gamemode = game["gamemode"],
            gametype = game["gametype"],
            numofplayers = game["numplayers"],
            players = game["players"],
            spectators = game["specs"],
            host = game["host"],
            port = game["port"]
        )

@orm.db_session
def get_gameinfo():
    if (uncached := SauertrackerGameService.get_uncached()):
        try:
            response = SauertrackerAPI.game(id=uncached.gameid, timeout=30)
        except Exception as e:
            return

        if not response:
            return

        if response.status_code != 200:
            return

        if SauertrackerGameInfoService.get_by_gameid(uncached.gameid):
            uncached.cached = True
            return


        print(f"[{getcurtime()}] Got game info of game {uncached.gameid}")

        SauertrackerGameInfoService.create(
            gameid=uncached.gameid,
            info=response.text
        )

        uncached.cached = True

@orm.db_session
def parse_demos():
    demos = sorted(glob.glob("demos/temp/*.dmo"))

    parser = DemoParser()

    for demo in demos:
        if UnprocessedDemoFileInfoService.get_by_path(demo):
            continue

        demo_mapname, demo_gamemode, demo_players, error = parser.parseDemo(filename=demo)

        if error:
            print(f"[{getcurtime()}] Encountered error: {error} while parsing demo {demo}")
            continue

        UnprocessedDemoFileInfoService.create(
            path=demo,
            mode=gamemodes[demo_gamemode],
            mapname=demo_mapname,
            players=str(demo_players)
        )

        print(f"[{getcurtime()}] Parsed demo {demo}")
        break

@orm.db_session
def match_demos():
    games = SauertrackerGameService.get_processable_games()

    if not games:
        return

    for game in games:
        if game.processed:
            continue

        demo_infos = UnprocessedDemoFileInfoService.get_by_mm(mode=game.gamemode, mapname=game.mapname)
        for demo_info in demo_infos:
            demo_players = ast.literal_eval(demo_info.players)
            if not (gameinfo := SauertrackerGameInfoService.get_by_gameid(gameid=game.gameid)):
                continue
            info = ast.literal_eval(gameinfo.info)
            players = info["players"]

            if len(players) <= 0:
                continue

            for player in players:
                if player["state"] == 5:  # Don't care about spectators
                    continue

                tmp_player = {
                    "name": player["name"],
                    "team": player["team"],
                    "frags": player["frags"],
                    "deaths": player["deaths"]
                }

                if frozenset(tmp_player.items()) not in demo_players:
                    continue

            print(f"[{getcurtime()}] Matched game {game.gameid} with demo {demo_info.path}")

            if not os.path.exists(demo_info.path):
                print(f"Demo {demo_info.path} doesn't exist")
            else:
                shutil.move(demo_info.path, f"demos/{game.gameid}.dmo")

                FinalDemoService.create(
                    gameid=game.gameid,
                    timestamp=game.timestamp,
                    mapname=game.mapname,
                    gamemode=game.gamemode,
                    gametype=game.gametype,
                    host=game.host,
                    port=game.port,
                    demo_path=f"demos/{game.gameid}.dmo",
                    serverdesc=info["description"]
                )

            game.processed = True
            demo_info.delete()
            return

@orm.db_session
def cleanup():
    demos = sorted(glob.glob("demos/temp/*.dmo"))

    for demo in demos:
        try:
            delta = (int(time.time())-os.path.getctime(demo))/3600
            # 36 hours
            if delta > 36:
                print(f"[{getcurtime()}] Cleanup: deleted {demo}")
                os.remove(demo)
                file_info = UnprocessedDemoFileInfoService.get_by_path(path=demo)
                if file_info:
                    file_info.delete()
        except FileNotFoundError:
            pass

    games = SauertrackerGameService.get_all()

    for game in games:
        delta = (int(time.time())-(game.timestamp))/3600
        # 36 hours
        if delta > 36:
            gameid = game.gameid
            print(f"[{getcurtime()}] Cleanup: deleted game {gameid} from db")
            game.delete()

            game_info = SauertrackerGameInfoService.get_by_gameid(gameid=gameid)
            if game_info:
                game_info.delete()


scheduler = BackgroundScheduler(daemon=True, timezone="Europe/Berlin", misfire_grace_time=None)
job = scheduler.add_job(check_for_new_games, "interval", seconds=35)
job = scheduler.add_job(get_gameinfo, "interval", seconds=35)
job = scheduler.add_job(parse_demos, "interval", seconds=10)
job = scheduler.add_job(match_demos, "interval", seconds=10)
job = scheduler.add_job(cleanup, "interval", seconds=10)
scheduler.start()
