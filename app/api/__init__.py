import pyperclip
from flask import Blueprint, jsonify, request

from app.utils.decorators import session_verify
from app.utils.error_respond import authentication_failure

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/clear_clipboard/', methods=['POST'])
@session_verify
def clear_clipboard():
    if request.decrypted_data == b'clear':
        pyperclip.copy('')
        return jsonify(message='Success')
    authentication_failure()
