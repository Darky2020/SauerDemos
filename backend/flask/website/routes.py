from flask import Blueprint, render_template

blueprint = Blueprint("website", __name__, url_prefix="/")

@blueprint.route("", methods=["GET"])
def index():
	return render_template("index.html")

@blueprint.route("search", methods=["GET"])
def search():
	return render_template("search.html")

@blueprint.route("api", methods=["GET"])
def api():
	return render_template("api.html")

@blueprint.route("about", methods=["GET"])
def about():
	return render_template("about.html")