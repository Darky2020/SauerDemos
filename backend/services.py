from .models import ServerPing, SauertrackerGame, SauertrackerGameInfo, DemolistCache, FinalDemo
from .models import SauerAuthKey, AuthToken, AdminPasswordHash, UnprocessedDemoFileInfo
from uuid import uuid4
from pony import orm
import requests
import bcrypt
import time
import json

SAUERTRACKER_API_BASE = "https://sauertracker.net/api"

class AdminPasswordHashService(object):
    @classmethod
    @orm.db_session
    def exists(cls):
        return (AdminPasswordHash.select().first() is not None)

    @classmethod
    @orm.db_session
    def create(cls, password):
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8") 

        return AdminPasswordHash(
                password_hash=password_hash
            )

    @classmethod
    @orm.db_session
    def validate(cls, password):
        return AdminPasswordHash.select().first().validate_password(password)

class AuthTokenService(object):
    @classmethod
    @orm.db_session
    def create(cls):
        if (tmp := AuthToken.select(valid=True).first()):
            tmp.valid = False

        uuid = str(uuid4())
        expires = int(time.time()) + 60*60
        return AuthToken(
                token=uuid,
                expires=expires,
                valid=True
            )

    @classmethod
    @orm.db_session
    def check_token(cls, uuid):
        token = AuthToken.select(token=uuid).first()
        if not token:
            return False

        if not token.valid:
            return False

        if token.expires < int(time.time()):
            token.valid = False
            return False

        return True


class SauerAuthKeyService(object):
    @classmethod
    @orm.db_session
    def create(cls, address, desc, name, key):
        return SauerAuthKey(
                address=address,
                desc=desc,
                name=name,
                key=key
            )

    @classmethod
    @orm.db_session
    def get_authkey(cls, address):
        return SauerAuthKey.select(address=address).first()

    @classmethod
    @orm.db_session
    def delete_key(cls, id_):
        try:
            SauerAuthKey[id_].delete()
            return 0
        except orm.core.ObjectNotFound:
            return 1

    @classmethod
    @orm.db_session
    def list(cls):
        return SauerAuthKey.select()

class SauertrackerAPI(object):
    @classmethod
    def servers(cls, timeout=1):
        try:
            return json.loads(requests.get(f"{SAUERTRACKER_API_BASE}/servers", timeout=timeout).text)
        except Exception:
            return None

    @classmethod
    def server(cls, host, port, timeout=1):
        try:
            return json.loads(requests.get(f"{SAUERTRACKER_API_BASE}/server/{host}/{port}", timeout=timeout).text)
        except Exception:
            return None

    @classmethod
    def server_activity(cls, host, port, timeout=1):
        try:
            return json.loads(requests.get(f"{SAUERTRACKER_API_BASE}/server/activity/{host}/{port}", timeout=timeout).text)
        except Exception:
            return None

    @classmethod
    def games(cls, host="", port="", serverdesc="", map="", gamemode="", gametype="", players="", fromdate="", todate="", limit=10, timeout=1):
        try:
            return json.loads(requests.get(f"{SAUERTRACKER_API_BASE}/games/find?host={host}&port={port}&serverdesc={serverdesc}&map={map}&gamemode={gamemode}&gametype={gametype}&players={players}&fromdate={fromdate}&todate={todate}&limit={limit}", timeout=timeout).text)["results"]
        except Exception:
            return None

    @classmethod
    def game(cls, id, timeout=1):
        try:
            return requests.get(f"{SAUERTRACKER_API_BASE}/game/{id}", timeout=timeout)
        except Exception as e:
            return None

class SauertrackerGameService(object):
    @classmethod
    @orm.db_session
    def create(cls, gameid, mapname, gamemode, gametype, numofplayers, players, spectators, host, port):
        return SauertrackerGame(
            gameid=gameid,
            timestamp=int(time.time()),
            mapname=mapname,
            gamemode=gamemode,
            gametype=gametype,
            numofplayers=numofplayers,
            players=players,
            specs=spectators,
            host=host,
            port=port,
            server_ping=ServerPingService.create(host, port)
        )

    @classmethod
    @orm.db_session
    def already_added(cls, gameid):
        game = orm.select(game for game in SauertrackerGame if game.gameid == gameid).first()
        try:
            return (game is not None)
        except Exception:
            return False

    @classmethod
    @orm.db_session
    def get_uncached(cls):
        return SauertrackerGame.select(
            lambda stg: not stg.cached
        ).first()

    @classmethod
    @orm.db_session
    def get_by_address(cls, host, port):
        return SauertrackerGame.select(
            lambda stg: stg.host == host and stg.port == port
        )

    @classmethod
    def get_by_mm(cls, mapname, mode):
        return SauertrackerGame.select(
            lambda stg: stg.mapname == mapname and stg.gamemode == mode
        )

    @classmethod
    def get_processable_games(cls):
        return SauertrackerGame.select(
            lambda stg: not stg.server_ping and stg.cached
        )

    @classmethod
    def get_all(cls):
        return SauertrackerGame.select(
            lambda stg: True
        )


class ServerPingService(object):
    @classmethod
    @orm.db_session
    def create(cls, host, port):
        server = orm.select(serv for serv in ServerPing if serv.host == host and serv.port == port).first()
        if server:
            return server
        else:
            return ServerPing(
                host=host,
                port=port,
                ignore=False,
                lastping=0,
            )

    @classmethod
    def servers(cls):
        return orm.select(s for s in ServerPing if True)

    @classmethod
    def get_by_address(cls, host, port):
        return ServerPing.select(
            lambda s: s.host == host and s.port == port
        ).first()

class SauertrackerGameInfoService(object):
    @classmethod
    @orm.db_session
    def create(cls, gameid, info):
        return SauertrackerGameInfo(
            gameid=gameid,
            info=info
        )

    @classmethod
    @orm.db_session
    def get_by_gameid(cls, gameid):
        return SauertrackerGameInfo.select(
            gameid=gameid
        ).first()

class DemolistCacheService(object):
    @classmethod
    @orm.db_session
    def create(cls, text):
        return DemolistCache(
            text=text
        )

    @classmethod
    @orm.db_session
    def get_by_text(cls, text):
        return DemolistCache.select(
            lambda d: d.text == text
        ).first()

class UnprocessedDemoFileInfoService(object):
    @classmethod
    @orm.db_session
    def create(cls, path, mode, mapname, players):
        return UnprocessedDemoFileInfo(
            path=path,
            mode=mode,
            mapname=mapname,
            players=players
        )

    @classmethod
    @orm.db_session
    def get_by_path(cls, path):
        return UnprocessedDemoFileInfo.select(
            lambda u: u.path == path
        )

    @classmethod
    @orm.db_session
    def get_by_mm(cls, mode, mapname):
        return UnprocessedDemoFileInfo.select(
            lambda u: u.mode == mode and u.mapname == mapname
        )

    @classmethod
    @orm.db_session
    def get_all(cls):
        return UnprocessedDemoFileInfo.select(
            lambda u: True
        )

class FinalDemoService(object):
    @classmethod
    @orm.db_session
    def create(cls, gameid, timestamp, mapname, gamemode, gametype, host, port, demo_path, serverdesc):
        return FinalDemo(
            gameid=gameid,
            timestamp=timestamp,
            mapname=mapname,
            gamemode=gamemode,
            gametype=gametype,
            host=host,
            port=port,
            demo_path=demo_path,
            serverdesc=serverdesc
        )

    @classmethod
    @orm.db_session
    def already_exists(cls, gameid):
        return (FinalDemo.select(gameid=gameid).first() is not None)

    @classmethod
    @orm.db_session
    def filter(cls, host=None, port=None, mapname=None, gamemode=None, gametype=None, beforetimestamp=None, aftertimestamp=None, beforeid=None, afterid=None, limit=10):
        if not beforeid and not afterid:
            beforeid = 99999999999

        if beforeid:
            return FinalDemo.select(
                lambda demo: (host == None or demo.host == host) and\
                (port == None or demo.port == port) and\
                (mapname == None or demo.mapname == mapname) and\
                (gamemode == None or demo.gamemode == gamemode) and\
                (gametype == None or demo.gametype == gametype) and\
                (demo.timestamp < beforetimestamp) and\
                (demo.timestamp > aftertimestamp) and\
                (demo.gameid < beforeid)
            ).order_by(orm.desc(FinalDemo.gameid))[:limit]
        else:
            return FinalDemo.select(
                lambda demo: (host == None or demo.host == host) and\
                (port == None or demo.port == port) and\
                (mapname == None or demo.mapname == mapname) and\
                (gamemode == None or demo.gamemode == gamemode) and\
                (gametype == None or demo.gametype == gametype) and\
                (demo.timestamp < beforetimestamp) and\
                (demo.timestamp > aftertimestamp) and\
                (demo.gameid > afterid)
            ).order_by(FinalDemo.gameid.asc)[:limit]




