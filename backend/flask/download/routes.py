from flask_limiter.util import get_remote_address
from backend.services import FinalDemoService
from flask_limiter import Limiter
from flask import send_file
from flask import Blueprint
from ..app import app
from pony import orm

limiter = Limiter(app, key_func=get_remote_address)
blueprint = Blueprint("download", __name__, url_prefix="/download/")

@blueprint.route("<name>", methods=["GET"])
@limiter.limit("30/minute;720/hour")
@orm.db_session
def download(name):
	return send_file(f"../../demos/{name}", attachment_filename=name)