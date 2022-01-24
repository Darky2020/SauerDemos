from webargs import fields, validate

authenticate = {
    "password": fields.Str(required=False)
}

addauthkey = {
	"address": fields.Str(required=True),
	"desc": fields.Str(required=True),
	"name": fields.Str(required=True),
	"key": fields.Str(required=True),
}

deleteauthkey = {
	"id": fields.Int(required=True)
}