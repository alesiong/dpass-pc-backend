import base64
import binascii
import random

from flask import Blueprint, current_app, jsonify, request, json

from app import SessionKey
from app.models import KeyLookupTable
from app.utils.cipher import encrypt_and_authenticate
from app.utils.decorators import session_verify, master_password_verify
from app.utils.master_password import MasterPassword

bp = Blueprint('api.password', __name__, url_prefix='/api/password')


@bp.route('/')
@session_verify
@master_password_verify
def get_table():
    key = SessionKey().session_key
    master_password: MasterPassword = current_app.config['MASTER_PASSWORD']
    hidden = request.args.get('hidden')
    if hidden:
        entries = KeyLookupTable.query.filter_by(hidden=False).all()
    else:
        entries = KeyLookupTable.query.all()

    entries = [
        {
            'key': entry.key,
            'metadata': json.loads(
                master_password.simple_decrypt(
                    base64.decodebytes(entry.meta_data.encode())).decode())
        } for entry in entries
    ]

    return SessionKey().encrypt_response(entries)


@bp.route('/persistent/', methods=['POST'])
@session_verify
# FIXME: this may not need to verify the master password
@master_password_verify
def persistent():
    data = json.loads(request.decrypted_data.decode())
    key = data["key"]
    persistence = current_app.config['STORAGE'].get(key, True)[1]
    return jsonify(result=persistence)


@bp.route('/get/', methods=['POST'])
@session_verify
@master_password_verify
def get():
    master_password: MasterPassword = current_app.config['MASTER_PASSWORD']
    data = json.loads(request.decrypted_data.decode())
    key = data["key"]
    # FIXME: what if key does not exist
    password_entry = base64.decodebytes(current_app.config['STORAGE'].get(key))
    return SessionKey().encrypt_response(master_password.decrypt(password_entry, key))


@bp.route('/new/', methods=['POST'])
@session_verify
@master_password_verify
def new():
    master_password: MasterPassword = current_app.config['MASTER_PASSWORD']
    new_key = random.random()
    while KeyLookupTable.query.filter_by(key=new_key).count() != 0:
        new_key = random.random()
    data = json.loads(request.decrypted_data.decode())
    KeyLookupTable.new_entry(new_key, data)
    current_app.config['STORAGE'].add(new_key, data)
    return new_key