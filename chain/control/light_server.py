from coincurve import PublicKey
from flask import Flask, Blueprint, request, jsonify, current_app

from app.utils.misc import base64_decode
from chain.control.controller import Controller
from chain.transaction import Transaction
from chain.utils.multiplexer import Multiplexer

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('transactions/', methods=['POST'])
def get_transactions():
    public_key = request.get_json()['account']
    account = PublicKey(base64_decode(public_key))
    controller: Controller = current_app.config['CONTROLLER']
    return jsonify(transactions=[(k.decode(), v.decode()) for k, v in controller.get_transactions(account)])


@bp.route('peers/')
def get_peers():
    controller: Controller = current_app.config['CONTROLLER']
    return jsonify(peers=[p.decode() for p in controller.get_peers()])


@bp.route('new_transaction', methods=['POST'])
def new_transaction():
    data = request.get_json()
    key = data['key'].encode()
    value = data['value'].encode()
    owner = base64_decode(data['owner'])  # bytes of compressed format public key
    serial = data['serial']  # integer
    signature = base64_decode(data['signature'])
    t = Transaction()
    t.key = key
    t.value = value
    t.owner = owner
    t.serial = serial
    t.signature = signature

    controller: Controller = current_app.config['CONTROLLER']

    result = controller.new_transaction_by_data(t.encode())
    return jsonify(result=result)


class Config:
    DEBUG = False


def light_server(rq, wq):
    app = Flask(__name__)
    app.config.from_object(Config())
    app.register_blueprint(bp)

    app.config['READ_QUEUE'] = rq
    app.config['WRITE_QUEUE'] = wq

    @app.before_first_request
    def startup():
        mx = Multiplexer(app.config['READ_QUEUE'], app.config['WRITE_QUEUE'])
        mx.start()
        app.config['CONTROLLER'] = Controller(mx)

    return app
