import os
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy

from config import configs

# Instantiate Flask extensions
db = SQLAlchemy()


def create_app(config_name='development'):
    """Create a Flask applicaction.
    """
    # Instantiate Flask
    app = Flask(__name__)

    app.config.from_object(configs[config_name])

    # Setup Flask-Extensions -- do this _after_ app config has been loaded

    # Setup Flask-SQLAlchemy
    db.init_app(app)

    # Register blueprints

    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    from app.views.demo import bp as demo_blueprint
    app.register_blueprint(demo_blueprint)

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

    return app
