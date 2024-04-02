from flask import (
    Blueprint, render_template, abort, current_app, request, redirect, url_for
)
from app.db import get_db
from app.utils import check_sorting, check_order
from math import ceil

bp = Blueprint('authors', __name__, url_prefix='/authors')

@bp.route('/<int:id>/')
def author(id):
    db = get_db()

    author = db.execute('SELECT * FROM all_authors WHERE id = ?', (id,)).fetchone()

    if not author:
        return abort(404)

    posts_per_page = current_app.config['POSTS_PER_PAGE'] or 24
    page = request.args.get('page', type=int)
    if not page:
        return redirect(url_for('authors.author', id=id, page=1), 308)

    sorting = check_sorting(request.args.get('sorting', 'uploaded_at', type=str))
    order = check_order(request.args.get('order', 'desc', type=str).upper())

    offset = (page - 1) * posts_per_page

    posts = db.execute(f'SELECT * FROM all_posts WHERE author_id = ? ORDER BY {sorting} {order} LIMIT ? OFFSET ?', (id, posts_per_page, offset)).fetchall()
    total_posts = db.execute(f'SELECT COUNT(*) FROM all_posts WHERE author_id = ?', (id,)).fetchone()[0]

    pagination = {
        "current_page": page,
        "total_pages": ceil(total_posts / posts_per_page)
    }

    if request.headers.get('X-Requested-With') == "XMLHttpRequest":
        return render_template('posts/xhr_section.html', posts=posts, pagination=pagination)

    return render_template("authors/author.html", author=author, posts=posts, pagination=pagination)