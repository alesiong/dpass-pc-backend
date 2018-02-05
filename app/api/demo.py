from flask import jsonify

from app.api import api


@api.route('/demo/<echo>')
def demo_get(echo):
    return jsonify(echo=echo)
