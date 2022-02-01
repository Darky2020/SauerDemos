from flask_limiter.util import get_remote_address
from backend.services import FinalDemoService
from webargs.flaskparser import use_args
from flask_limiter import Limiter
from .args import demosfind_args
from flask import Blueprint
from ..app import app
from pony import orm

limiter = Limiter(app, key_func=get_remote_address)
blueprint = Blueprint("api", __name__, url_prefix="/api/")

@blueprint.route("/demos/find", methods=["GET", "POST"])
@use_args(demosfind_args, location="querystring")
@limiter.limit("480/minute;2400/hour")
@orm.db_session
def find(args):
    result = {"error": None, "data": {}}

    result["data"]["result"] = []

    demos = FinalDemoService.filter(
    	host=args["host"],
    	port=args["port"],
    	mapname=args["mapname"],
    	gamemode=args["gamemode"],
    	gametype=args["gametype"],
    	beforetimestamp=args["beforetimestamp"],
    	aftertimestamp=args["aftertimestamp"],
    	beforeid=args["beforeid"], 
        afterid=args["afterid"], 
    	limit=args["limit"]
    )

    for demo in demos:
    	result["data"]["result"].append(
    		{
    			"gameid": demo.gameid,
				"timestamp": demo.timestamp,
				"mapname": demo.mapname,
				"gamemode": demo.gamemode,
				"gametype": demo.gametype,
				"host": demo.host,
				"port": demo.port,
				"download_link": f"/download/{demo.gameid}.dmo",
				"sauertracker_link": f"https://sauertracker.net/game/{demo.gameid}",
                "serverdesc": demo.serverdesc
    		}
    	)

    return result