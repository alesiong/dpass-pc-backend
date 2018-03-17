import base64

from flask import Blueprint, current_app, jsonify, request, json

from app import SessionKey
from app.models import KeyLookupTable
from app.utils import error_respond
from app.utils.decorators import session_verify, master_password_verify
from app.utils.master_password import MasterPassword

bp = Blueprint('api.password', __name__, url_prefix='/api/password')


@bp.route('/')
@master_password_verify
def get_table():
    hidden = request.args.get('hidden')
    master_password: MasterPassword = current_app.config['MASTER_PASSWORD']
    storage = current_app.config['STORAGE']

    if hidden:
        entries = KeyLookupTable.query.all()
    else:
        entries = KeyLookupTable.query.filter_by(hidden=False).all()

    new_entries = sum(entry for entry in entries if entry.meta_data == '')

    if master_password.check_expire(len(entries) + len(new_entries) * 2):
        error_respond.master_password_expired()

    for new_entry in new_entries:
        encrypted = storage.get(new_entry.key)
        if encrypted:
            metadata = json.loads(
                master_password.decrypt(
                    base64.decodebytes(encrypted.encode()),
                    new_entry.key).decode())
            del metadata['password']
            metadata = base64.encodebytes(master_password.simple_encrypt(json.dumps(metadata))).decode()
            new_entry.meta_data = metadata

    KeyLookupTable.query.session.commit()

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
@master_password_verify(2)
def new():
    master_password: MasterPassword = current_app.config['MASTER_PASSWORD']
    data = json.loads(request.decrypted_data.decode())

    try:
        del data['password']
    except KeyError:
        # ignore it if the `password` entry is not provided
        pass
    data = master_password.simple_encrypt(json.dumps(data))

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
