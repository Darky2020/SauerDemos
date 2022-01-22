from backend.services import AdminPasswordHashService, AuthTokenService, SauerAuthKeyService
from flask import Blueprint, make_response, request
from webargs.flaskparser import use_args
from .decorators import token_required
from . import args

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

@blueprint.route("/authkey/add", methods=["POST"])
@use_args(args.addauthkey, location="json")
@token_required
def addauthkey(args):
	SauerAuthKeyService.create(args["address"], args["desc"], args["name"], args["key"])

	return "Key added", 200

@blueprint.route("/authkey/delete", methods=["POST"])
@use_args(args.deleteauthkey, location="json")
@token_required
def deleteauthkey(args):
	if SauerAuthKeyService.delete_key(args["id"]):
		return f"Key with id {args['id']} doesn't exist", 400

	return "Key deleted", 200
