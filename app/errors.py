from flask import Blueprint, render_template

bp = Blueprint('errors', __name__)

@bp.app_errorhandler(400)
def bad_request(e):
    return render_template('errors/400.html'), 400

@bp.app_errorhandler(401)
def unauthorized(e):
    return render_template('errors/401.html'), 401

@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500