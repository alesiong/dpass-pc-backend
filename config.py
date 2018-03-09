# project/server/config.py

import os

import datetime

basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db')


class BaseConfig(object):
    """Base configuration."""
    DEBUG = False
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PREFERRED_URL_SCHEME = 'https'

    IS_ONLINE = False

    INIT_STATE = 0  # 0: not initialized, 1: initializing, 2: initialized

    MASTER_PASSWORD_EXPIRY = datetime.timedelta(minutes=10)
    SETTINGS_FILE = 'db/settings.json'

    USE_ETHEREUM = False


class DevelopmentTestConfig(BaseConfig):
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4


class DevelopmentConfig(DevelopmentTestConfig):
    """Development configuration."""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    DEBUG_TB_ENABLED = True


class TestingConfig(DevelopmentTestConfig):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    DEBUG_TB_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'storage.db')
    DEBUG_TB_ENABLED = False


configs = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
