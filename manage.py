#!/usr/bin/env python

"""This file sets up a command line manager.

Use "python manage.py" for a list of available commands.
Use "python manage.py runserver" to start the development web server on localhost:5000.
Use "python manage.py runserver --help" for additional runserver options.
"""
import unittest

from flask_migrate import MigrateCommand
from flask_script import Manager, Shell, Server

from app import create_app, db

# Setup Flask-Script with command line commands
app = create_app()
manager = Manager(app)


@manager.command
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


manager.add_command('db', MigrateCommand)
manager.add_command("shell", Shell(make_context=lambda: dict(app=app, db=db)))
manager.add_command('runserver', Server(threaded=True))

if __name__ == "__main__":
    # python manage.py                      # shows available commands
    # python manage.py runserver --help     # shows available runserver options
    manager.run()
