from backend.services import AdminPasswordHashService, AuthTokenService, SauerAuthKeyService, SauerPasswordService, FinalDemoService
from flask import Blueprint, make_response, request
from webargs.flaskparser import use_args
from .decorators import token_required
from pony import orm
from . import args
import json
import glob
import os

blueprint = Blueprint("auth", __name__, url_prefix="/auth/")

@blueprint.route("/authenticate", methods=["POST"])
@use_args(args.authenticate, location="json")
def authenticate(args):
	if not AdminPasswordHashService.validate(args["password"]):
		return "Invalid password", 400

	token = AuthTokenService.create()

	resp = make_response()
	resp.set_cookie('AuthToken', token.token, max_age=60*60)

	return resp, 200

@blueprint.route("/info", methods=["GET"])
@token_required
def info():
	demos = glob.glob("demos/*.dmo")
	tmp_demos = glob.glob("demos/temp/*.dmo")
	demos_size = 0
	tmp_demos_size = 0

	for demo in demos:
		demos_size += os.stat(f"{demo}").st_size

	for tmp_demo in tmp_demos:
		tmp_demos_size += os.stat(f"{tmp_demo}").st_size

	resp = {
		"num_of_demos": len(demos),
		"num_of_temp_demos": len(tmp_demos),
		"size_of_demos": f"{round(demos_size/(1024**3), 2)} GB",
		"size_of_temp_demos": f"{round(tmp_demos_size/(1024**2), 2)} MB"
	}

	return resp, 200

@blueprint.route("/authkey/add", methods=["POST"])
@use_args(args.addauthkey, location="json")
@token_required
def addauthkey(args):
	SauerAuthKeyService.create(args["address"], args["desc"], args["name"], args["key"])

	return "Key added", 200

@blueprint.route("/authkey/list", methods=["GET"])
@token_required
@orm.db_session
def listauthkey():
	data = []
	authkeys = SauerAuthKeyService.list()
	for authkey in authkeys:
		data.append({
				"id": authkey.id,
				"address": authkey.address,
				"desc": authkey.desc,
				"name": authkey.name
			})

	return json.dumps(data), 200

@blueprint.route("/authkey/delete", methods=["POST"])
@use_args(args.deleteauthkey, location="json")
@token_required
def deleteauthkey(args):
	if SauerAuthKeyService.delete_key(args["id"]):
		return f"Key with id {args['id']} doesn't exist", 400

	return "Key deleted", 200

@blueprint.route("/password/add", methods=["POST"])
@use_args(args.addpassword, location="json")
@token_required
def addpassword(args):
	SauerPasswordService.create(args["address"], args["password"])

	return "Password added", 200

@blueprint.route("/password/list", methods=["GET"])
@token_required
@orm.db_session
def listpassword():
	data = []
	passwords = SauerPasswordService.list()
	for password in passwords:
		data.append({
				"id": password.id,
				"address": password.address
			})

	return json.dumps(data), 200

@blueprint.route("/password/delete", methods=["POST"])
@use_args(args.deletepassword, location="json")
@token_required
def deletepassword(args):
	if SauerPasswordService.delete_password(args["id"]):
		return f"Password with id {args['id']} doesn't exist", 400

	return "Password deleted", 200

@blueprint.route("/demo/remove", methods=["POST"])
@use_args(args.removedemo, location="json")
@token_required
def removedemo(args):
	if not FinalDemoService.remove_by_gameid(args["gameid"]):
		return f"Couldn't remove demo {args['gameid']}", 400

	return "Removed demo", 200
