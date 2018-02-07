# project/server/config.py

import os

from app.utils.local_storage import LocalStorage

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    """Base configuration."""
    DEBUG = False
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PREFERRED_URL_SCHEME = 'https'

    IS_ONLINE = False

    STORAGE_CLASS = LocalStorage
    INIT_STATE = 0  # 0: not initialized, 1: initializing, 2: initialized


class DevelopmentTestConfig(BaseConfig):
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    WTF_CSRF_ENABLED = False


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
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-production.sqlite')
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False


configs = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
