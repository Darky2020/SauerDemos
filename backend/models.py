from pony import orm
import bcrypt

db = orm.Database()

db.bind(provider="sqlite", filename="../database.db", create_db=True)

class AdminPasswordHash(db.Entity):
	password_hash = orm.Required(str)

	def validate_password(self, password):
		return bcrypt.checkpw(
			password.encode("utf-8"), self.password_hash.encode("utf-8")
		)

class AuthToken(db.Entity):
	token = orm.Required(str)
	expires = orm.Required(int)
	valid = orm.Required(bool)

class SauerAuthKey(db.Entity):
    address = orm.Required(str)
    desc = orm.Required(str)
    name = orm.Required(str)
    key = orm.Required(str)

class SauerPassword(db.Entity):
    address = orm.Required(str)
    password = orm.Required(str)

class ServerPing(db.Entity):
    ignore = orm.Required(bool)
    host = orm.Required(str)
    port = orm.Required(int)
    games = orm.Set("SauertrackerGame")
    lastping = orm.Required(int)

class SauertrackerGame(db.Entity):
    gameid = orm.Required(int)
    timestamp = orm.Required(int)
    mapname = orm.Required(str)
    gamemode = orm.Required(str)
    gametype = orm.Required(str)
    numofplayers = orm.Required(int)
    players = orm.Required(str)
    specs = orm.Optional(str)
    host = orm.Required(str)
    port = orm.Required(int)
    server_ping = orm.Optional("ServerPing")
    cached = orm.Required(bool, default=False)
    processed = orm.Required(bool, default=False)

    def __str__(self):
        return f"SauertrackerGame({self.gameid}, {self.timestamp}, {self.mapname}, {self.gamemode}, {self.gametype}, {self.numofplayers}, {self.players}, {self.specs}, {self.host}, {self.port})"

class SauertrackerGameInfo(db.Entity):
    gameid = orm.Required(int)
    info = orm.Required(str)

    def __str__(self):
        return f"SauertrackerGameInfo({self.gameid}, {self.info})"

class DemolistCache(db.Entity):
    text = orm.Required(str)

class UnprocessedDemoFileInfo(db.Entity):
    path = orm.Required(str)
    mode = orm.Required(str)
    mapname = orm.Required(str)
    players = orm.Required(str)

    def __str__(self):
        return f"UnprocessedDemoFileInfo({self.path}, {self.mode}, {self.mapname}, {self.players})"

class FinalDemo(db.Entity):
    gameid = orm.Required(int, unique=True)
    timestamp = orm.Required(int)
    mapname = orm.Required(str)
    gamemode = orm.Required(str)
    gametype = orm.Required(str)
    host = orm.Required(str)
    port = orm.Required(int)
    serverdesc = orm.Required(str)
    demo_path = orm.Required(str)

    def __str__(self):
        return f"FinalDemo({self.gameid}, {self.timestamp}, {self.mapname}, {self.gamemode}, {self.gametype}, {self.host}, {self.port}, {self.demo_path})"

db.generate_mapping(create_tables=True)