import json
import os

from flask import Flask, url_for, render_template, redirect
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from web3 import Web3, IPCProvider

from app.utils.ethereum_utils import EthereumUtils
from app.utils.local_storage import LocalStorage
from app.utils.misc import get_env, get_ipc
from app.utils.session_key import SessionKey
from app.utils.settings import Settings
from config import configs

# Instantiate Flask extensions
db = SQLAlchemy()
socketio = SocketIO()


def create_app(config_name='development', queue=None, use_storage=None):
    """
    Create a Flask applicaction.
    """
    # Instantiate Flask
    app = Flask(__name__)

    app.config.from_object(configs[config_name])

    # Setup Flask-Extensions -- do this _after_ app config has been loaded

    # Setup Flask-SQLAlchemy
    db.init_app(app)
    socketio.init_app(app)

    # Register blueprints

    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    from app.api.session import bp as session_blueprint
    app.register_blueprint(session_blueprint)

    from app.api.master_password import bp as master_password_blueprint
    app.register_blueprint(master_password_blueprint)

    from app.api.settings import bp as settings_blueprint
    app.register_blueprint(settings_blueprint)

    from app.api.password import bp as password_blueprint
    app.register_blueprint(password_blueprint)

    # Jinja2 Filters
    app.jinja_env.filters['str'] = str

    if config_name == 'production':
        pass
    else:
        @app.context_processor
        def override_url_for():
            return dict(url_for=dated_url_for)

        def dated_url_for(endpoint, **values):
            if endpoint == 'static':
                filename = values.get('filename', None)
                if filename:
                    file_path = os.path.join(app.root_path,
                                             endpoint, filename)
                    values['q'] = int(os.stat(file_path).st_mtime)
            return url_for(endpoint, **values)

    app.config['QUEUE'] = queue
    if use_storage == 'ethereum':
        app.config['USE_ETHEREUM'] = True

    @app.before_first_request
    def startup():
        if app.config['QUEUE']:
            SessionKey(app.config['QUEUE'].get())

        if app.config['USE_ETHEREUM']:
            ethereum_utils = EthereumUtils(Web3(IPCProvider(get_ipc('./ethereum_private/data', 'geth.ipc'))))
            storage_factory_abi = json.load(open('./ethereum_private/contracts/storage_factory.abi.json'))
            storage_abi = json.load(open('./ethereum_private/contracts/storage.abi.json'))
            ethereum_utils.init_contracts(get_env()['ETH_STORAGE'], storage_factory_abi, storage_abi)

        Settings(app.config['SETTINGS_FILE'])

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def index(path):
        return render_template('page/index.html')

    @app.route('/favicon.ico')
    def favicon():
        return redirect(url_for('static', filename='images/favicon.ico'))

    return app, socketio
