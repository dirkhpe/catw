import os
# basedir = os.path.abspath(os.path.dirname(__file__))
# print('Basedir: {b}'.format(b=basedir))

# Be careful: Variable names need to be UPPERCASE


class Config:
    SECRET_KEY = os.urandom(24)

    # Config values from flaskrun.ini
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:Monitor1@localhost/fl_catw"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # pythonanywhere disconnects clients after 5 minutes idle time. Set pool_recycle to avoid disconnection
    # errors in the log: https://help.pythonanywhere.com/pages/UsingSQLAlchemywithMySQL (from: PythonAnywhere -
    # some tips for specific web frameworks: Flask
    SQLALCHEMY_POOL_RECYCLE = 280

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    LOGLEVEL = "debug"
    # SERVER_NAME = '0.0.0.0:5012'
    SERVER_NAME = 'localhost:5123'
    SQLALCHEMY_DATABASE_URI = "sqlite:///C:\\Development\\python\\catw\\catw\\data\\catw.db"
    LOGDIR = "C:\\Temp\\Log"


class TestingConfig(Config):
    DEBUG = False
    # Set Loglevel to warning or worse (error, fatal) for readability
    LOGLEVEL = "error"
    TESTING = True
    SECRET_KEY = 'The Secret Test Key!'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost:5999'
    SQLALCHEMY_DATABASE_URI = "sqlite:///C:\\Development\\python\\catw\\catw\\data\\catw.db"
    LOGDIR = "C:\\Temp\\Log"


class ProductionConfig(Config):
    ADMINS = ['dirk@vermeylen.net']
    LOGLEVEL = "warning"
    # SERVER_NAME = 'localhost:5008'
    DEBUG = False
    LOGDIR = "/var/sites/cats"
    SQLALCHEMY_DATABASE_URI = "sqlite:////home/dirk/cats/catw/data/catw.db"

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
