from coincurve import PublicKey
from flask import Flask, Blueprint, request, jsonify, current_app

from app.utils.misc import base64_decode
from chain.control.controller import Controller
from chain.utils.multiplexer import Multiplexer

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/transactions/', methods=['POST'])
def get_transactions():
    public_key = request.get_json()['account']
    account = PublicKey(base64_decode(public_key))
    controller: Controller = current_app.config['CONTROLLER']
    return jsonify(transactions=[(k.decode(), v.decode()) for k, v in controller.get_transactions(account)])


class Config:
    DEBUG = False


def light_server(rq, wq):
    mx = Multiplexer(rq, wq)
    mx.start()

    app = Flask(__name__)
    app.config.from_object(Config())
    app.register_blueprint(bp)

    app.config['CONTROLLER'] = Controller(mx)

    return app

    # app.run(port=3600)
