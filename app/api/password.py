import base64
import random

from flask import Blueprint, current_app, jsonify, request, json

from app import SessionKey
from app.models import KeyLookupTable
from app.utils import error_respond
from app.utils.decorators import session_verify, master_password_verify
from app.utils.master_password import MasterPassword

bp = Blueprint('api.password', __name__, url_prefix='/api/password')


@bp.route('/')
@session_verify
@master_password_verify
def get_table():
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
    try:
        key = data["key"]
    except KeyError:
        return error_respond.invalid_post_data()
    persistence = current_app.config['STORAGE'].get(key, True)[1]
    if persistence is not None:
        return jsonify(result=persistence)
    else:
        return error_respond.key_not_found()


@bp.route('/get/', methods=['POST'])
@session_verify
@master_password_verify
def get():
    master_password: MasterPassword = current_app.config['MASTER_PASSWORD']
    data = json.loads(request.decrypted_data.decode())
    try:
        key = data["key"]
    except KeyError:
        return error_respond.invalid_post_data()
    get_password = current_app.config['STORAGE'].get(key)
    if get_password is not None:
        password_entry = base64.decodebytes(get_password.encode())
        return SessionKey().encrypt_response(master_password.decrypt(password_entry, key))
    else:
        return error_respond.key_not_found()


# FIXME: catch database error

@bp.route('/new/', methods=['POST'])
@session_verify
@master_password_verify
def new():
    master_password: MasterPassword = current_app.config['MASTER_PASSWORD']
    data = json.loads(request.decrypted_data.decode())

    try:
        del data['password']
    except KeyError:
        # ignore it if the `password` entry is not provided
        pass
    data = master_password.simple_encrypt(json.dumps(data).encode())
    entry = KeyLookupTable.new_entry(base64.encodebytes(data).decode())
    current_app.config['STORAGE'].add(entry.key,
                                      base64.encodebytes(
                                          master_password.encrypt(request.decrypted_data.decode(), entry.key)).decode())
    return SessionKey().encrypt_response({'key': entry.key})


@bp.route('/modify/', methods=['POST'])
@session_verify
@master_password_verify
def modify():
    master_password: MasterPassword = current_app.config['MASTER_PASSWORD']


@bp.route('/delete/', methods=['POST'])
@session_verify
@master_password_verify
def delete():
    storage = current_app.config['STORAGE']
    data = json.loads(request.decrypted_data.decode())

    key = data.get('key')
    if key is None:
        error_respond.invalid_post_data()
    if storage.get(key) is None:
        error_respond.key_not_found()

    current_app.config['STORAGE'].delete(key)
    KeyLookupTable.query.filter_by(key=key).delete()
    KeyLookupTable.query.session.commit()
    return jsonify(message='Success')


@bp.route('/mark/', methods=['POST'])
@session_verify
@master_password_verify
def mark():
    data = json.loads(request.decrypted_data.decode())
    key = data.get('key')
    if key is None:
        error_respond.invalid_post_data()
    if 'hidden' not in data:
        error_respond.invalid_post_data()
    entry = KeyLookupTable.query.filter_by(key=key).first()
    entry.hidden = data['hidden']
    KeyLookupTable.query.session.commit()
    return jsonify(message='Success')
