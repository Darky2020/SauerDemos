from flask_limiter.util import get_remote_address
from backend.services import FinalDemoService
from flask_limiter import Limiter
from datetime import datetime
from flask import send_file
from flask import Blueprint
from ..app import app
from pony import orm

limiter = Limiter(app, key_func=get_remote_address)
blueprint = Blueprint("download", __name__, url_prefix="/download/")

@blueprint.route("<name>", methods=["GET"])
@limiter.limit("240/minute;3600/hour")
@orm.db_session
def download(name):
	demo = FinalDemoService.get_by_gameid(int(name[:-4]))

	datetime_string = datetime.utcfromtimestamp(demo.timestamp).isoformat().replace(":", "-").replace(" ", "_")
	gamemode = demo.gamemode
	gametype = demo.gametype
	mapname = demo.mapname
	servdesc = demo.serverdesc

	return send_file(f"../../demos/{name}", attachment_filename=f"{datetime_string}_{gamemode}_{mapname}_{gametype}_{servdesc}.dmo")