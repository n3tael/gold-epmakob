from flask import Blueprint, Response, abort, make_response
from app.db import get_db

bp = Blueprint('images', __name__, url_prefix='/images')

@bp.route('/<int:id>.webp')
def image(id):
    db = get_db()

    image = db.execute("SELECT image FROM images WHERE id = ?", (id,)).fetchone()
    if not image:
        abort(404)

    response = make_response(Response(image, mimetype='image/webp'))
    response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response