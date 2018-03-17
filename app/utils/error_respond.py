from flask import abort, jsonify, make_response


def authentication_failure():
    abort(make_response(jsonify(error='Authentication Failure'), 401))


def master_password_wrong():
    abort(make_response(jsonify(error='Master Password Wrong'), 401))


def master_password_expired():
    abort(make_response(jsonify(error='Master Password Expired'), 401))


def invalid_post_data():
    abort(make_response(jsonify(error='Invalid POST Data'), 400))


def invalid_arguments():
    abort(make_response(jsonify(error='Invalid Arguments'), 400))


def master_password_already_set():
    abort(make_response(jsonify(error='Master Password Already set'), 400))


def key_not_found():
    abort(make_response(jsonify(error='Key Not Found'), 400))


def blockchain_account_wrong():
    abort(make_response(jsonify(error='Blockchain Account Wrong'), 400))
