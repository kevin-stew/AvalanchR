from flask import Flask
from flask_migrate import Migrate
from config import Config

from .site.routes import site
from .authentication.routes import auth
from .models import db as root_db, login_manager, ma

app = Flask(__name__)

# set TOTAL MAX for all files uploaded at onec (image + 3Dmodel)
app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024

app.config.from_object(Config)

app.register_blueprint(site)
app.register_blueprint(auth)

root_db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login' #specify the page rendered for non-authed users
ma.init_app(app)
migrate = Migrate(app, root_db)


if __name__ == "__main__":
    app.run()