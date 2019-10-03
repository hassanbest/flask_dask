import os
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.getcwd()}/app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'dont_tell_anyone'
