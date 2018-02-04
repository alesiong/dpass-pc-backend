from flask import Blueprint, render_template

bp = Blueprint('pages', __name__, url_prefix='/pages')


@bp.route('/demo/')
def demo():
    return render_template('page/demo.html')
