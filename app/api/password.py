from typing import Union

from flask import Blueprint, current_app, jsonify, request, json

from app import SessionKey
from app.models import KeyLookupTable
from app.utils import error_respond
from app.utils.decorators import session_verify, master_password_verify
from app.utils.master_password import MasterPassword
from app.utils.misc import base64_decode, base64_encode

bp = Blueprint('api.password', __name__, url_prefix='/api/password')


def simple_decrypt_then_json(master_password: MasterPassword, data: Union[str, bytes]) -> Union[dict, list]:
    if isinstance(data, str):
        data = base64_decode(data)
    return json.loads(master_password.simple_decrypt(data).decode())


def simple_encrypt_from_dict(master_password: MasterPassword, data: Union[dict, list]) -> bytes:
    return master_password.simple_encrypt(json.dumps(data))


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

    new_entries = [entry for entry in entries if entry.meta_data == '']

    if master_password.check_expire(len(entries) + len(new_entries) * 2):
        error_respond.master_password_expired()

    for new_entry in new_entries:
        encrypted: str = storage.get(new_entry.key)
        if encrypted:
            metadata = json.loads(
                master_password.decrypt(
                    base64_decode(encrypted),
                    new_entry.key).decode())
            del metadata['password']
            metadata = base64_encode(simple_encrypt_from_dict(metadata))
            new_entry.meta_data = metadata

    KeyLookupTable.query.session.commit()

    entries = [
        {
            'key': entry.key,
            'hidden': entry.hidden,
            'metadata': simple_decrypt_then_json(master_password, entry.meta_data)
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
        password_entry = base64_decode(get_password)
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

    entry = KeyLookupTable.new_entry(base64_encode(simple_encrypt_from_dict(master_password, data)))
    current_app.config['STORAGE'].add(entry.key,
                                      base64_encode(
                                          master_password.encrypt(request.decrypted_data.decode(), entry.key)))
    return SessionKey().encrypt_response({'key': entry.key})


@bp.route('/modify/', methods=['POST'])
@session_verify
@master_password_verify(4)
def modify():
    master_password: MasterPassword = current_app.config['MASTER_PASSWORD']
    data = json.loads(request.decrypted_data.decode())
    modify_key = data.get('key')
    if modify_key is None or 'modified' not in data:
        error_respond.invalid_post_data()
    entry = KeyLookupTable.query.get(modify_key)
    if entry is None:
        error_respond.key_not_found()
    password = data['modified'].get('password')
    if password:
        del data['modified']['password']

    # modify metadata
    metadata = simple_decrypt_then_json(master_password, entry.meta_data)
    for k in data['modified']:
        metadata[k] = data['modified'][k]
    entry.meta_data = base64_encode(simple_encrypt_from_dict(master_password, metadata))
    KeyLookupTable.query.session.commit()

    # modify storage
    storage = current_app.config['STORAGE']
    encrypted = storage.get(modify_key)

    password_data = json.loads(
        master_password.decrypt(
            base64_decode(encrypted),
            modify_key).decode())
    for k in data['modified']:
        password_data[k] = data['modified'][k]
    if password:
        password_data['password'] = password

    storage.add(modify_key,
                base64_encode(
                    master_password.encrypt(json.dumps(password_data), modify_key)))
    return SessionKey().encrypt_response({'key': modify_key})


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
    entry = KeyLookupTable.query.get(key)
    if entry is None:
        error_respond.key_not_found()
    entry.hidden = data['hidden']
    KeyLookupTable.query.session.commit()
    return jsonify(message='Success')
