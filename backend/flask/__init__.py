from .download import download
from .website import website
from .auth import auth
from .api import api
from .app import app

app.register_blueprint(api)
app.register_blueprint(auth)
app.register_blueprint(website)
app.register_blueprint(download)