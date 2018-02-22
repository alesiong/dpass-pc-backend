from flask import abort, jsonify, make_response


def authentication_failure():
    abort(make_response(jsonify(error='Authentication Failure'), 401))


def invalid_post_data():
    abort(make_response(jsonify(error='Invalid POST Data'), 400))
