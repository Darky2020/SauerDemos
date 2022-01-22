from webargs import fields, validate

demosfind_args = {
    "host": fields.Str(missing=None),
    "port": fields.Int(missing=None),
    "mapname": fields.Str(missing=None),
    "gamemode": fields.Str(missing=None),
    "gametype": fields.Str(missing=None),
    "beforetimestamp": fields.Int(missing=99999999999),
    "aftertimestamp": fields.Int(missing=0),
    "beforeid": fields.Int(missing=None),
    "afterid": fields.Int(missing=None),
    "limit": fields.Int(
        missing=10, validate=[
            validate.Range(
                min=1, max=1000
            )
        ]
    )
}