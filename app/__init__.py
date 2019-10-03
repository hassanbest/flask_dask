import os

from flask import Flask, send_from_directory
from flask.helpers import get_root_path
from flask_login import login_required

from app.models import User
from config import BaseConfig


def register_dashapps(app):
    from app.dashapp1.app import create_dash_app
    from app.dashapp1.app import register_callbacks

    # Meta tags for viewport responsiveness
    meta_viewport = {"name": "viewport", "content": "width=100%, initial-scale=1, shrink-to-fit=no"}

    dashapp1 = create_dash_app(__name__, app, '/dashboard/',
                                get_root_path(__name__)+'/dashboard/assets/', [meta_viewport])

    with app.app_context():
        dashapp1.title = 'Dashapp 1'
        register_callbacks(dashapp1)

    _protect_dashviews(dashapp1)


def _protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(dashapp.server.view_functions[view_func])


def register_extensions(server):
    from app.extensions import db
    from app.extensions import login
    from app.extensions import migrate

    db.init_app(server)
    login.init_app(server)
    login.login_view = 'main.login'
    migrate.init_app(server, db)


def register_blueprints(server):
    from app.webapp import server_bp
    server.register_blueprint(server_bp)


server = Flask(__name__)
server.config.from_object(BaseConfig)
register_dashapps(server)
register_extensions(server)
register_blueprints(server)