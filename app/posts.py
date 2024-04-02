from flask import (
    Blueprint, current_app, redirect, render_template, request, abort, make_response, url_for
)
from datetime import datetime, timezone
from app.utils import check_sorting, check_order
from app.db import get_db
from math import ceil
import random
import secrets

bp = Blueprint('posts', __name__, url_prefix='/posts')

def generate_new_token(db):
    new_token = secrets.token_urlsafe(24)

    db.execute("INSERT INTO tokens (token) VALUES (?)", (new_token,))
    db.commit()

    return new_token

def make_sql_filters(only_voted, token, author_id, only_with_caption, sorting, order):
    if only_voted:
        filters = f"LEFT JOIN votes ON votes.token = '{token}' WHERE votes.post_id = id"
    elif author_id or only_with_caption:
        filters = "WHERE "
    else:
        filters = ""

    if only_voted and author_id:
        filters += " AND "

    if author_id:
        filters += f"all_posts.author_id = {author_id}"

    if author_id and only_with_caption:
        filters += " AND "

    if only_with_caption:
        filters += "all_posts.caption IS NOT NULL"

    filters += f" ORDER BY {sorting} {order}"
    return filters

@bp.route('/')
def all_posts():
    db = get_db()

    token = request.cookies.get('token', type=str)
    token_in_db = db.execute('SELECT * FROM tokens WHERE token = ?', (token,)).fetchone();
    if not token_in_db:
        token = generate_new_token(db)

    posts_per_page = current_app.config['POSTS_PER_PAGE'] or 24
    page = request.args.get('page', type=int)
    if not page:
        return redirect(url_for('posts.all_posts', page=1), 308)

    sorting = check_sorting(request.args.get('sorting', 'uploaded_at', type=str))
    order = check_order(request.args.get('order', 'desc', type=str).upper())

    author_id = request.args.get('author_id', type=int)
    only_with_caption = request.args.get('with_caption', False, type=bool)
    only_voted = request.args.get('only_voted', False, type=bool)

    offset = (page - 1) * posts_per_page

    filters_and_sorting = make_sql_filters(only_voted, token, author_id, only_with_caption, sorting, order)

    posts = db.execute(f'SELECT * FROM all_posts {filters_and_sorting} LIMIT ? OFFSET ?', (posts_per_page, offset)).fetchall()
    total_posts = db.execute(f'SELECT COUNT(*) FROM all_posts {filters_and_sorting}').fetchone()[0]

    authors = db.execute('SELECT id, name FROM authors').fetchall()

    pagination = {
        "current_page": page,
        "total_pages": ceil(total_posts / posts_per_page)
    }

    if request.headers.get('X-Requested-With') == "XMLHttpRequest":
        return render_template('posts/xhr_section.html', posts=posts, pagination=pagination)

    return render_template('posts/all.html', authors=authors, posts=posts, pagination=pagination)

@bp.route('/random/')
def random_post():
    db = get_db()

    posts_ids = db.execute(f'SELECT id FROM posts').fetchall()
    ids = []

    for id in posts_ids:
        ids.append(id[0])

    id = random.choice(ids)

    return redirect(url_for('posts.post', id=id), 303)

@bp.get('/<int:id>/')
def post(id):
    db = get_db()

    token = request.cookies.get('token')
    token_in_db = db.execute('SELECT * FROM tokens WHERE token = ?', (token,)).fetchone();
    if not token_in_db:
        token = generate_new_token(db)

    post = db.execute('''
                        SELECT all_posts.*, CASE
                            WHEN votes.post_id THEN 1 ELSE 0
                        END AS is_voted
                        FROM all_posts
                        LEFT JOIN votes ON votes.post_id = id AND votes.token = ?
                        WHERE id = ?
                    ''', (token, id,)).fetchone();
    if not post: abort(404)

    images = db.execute('SELECT * FROM images WHERE post_id = ?;', (post[0],)).fetchall()

    response = make_response(render_template('posts/post.html', post=post, images=images))
    if not token_in_db: response.set_cookie(key="token", value=token, max_age=60*60*24*365*2, secure=True)
    return response

@bp.post('/<int:id>/')
def post_vote(id):
    db = get_db()

    if not db.execute('SELECT id FROM posts WHERE id = ?', (id,)).fetchone()[0]:
        return abort(404)

    token = request.cookies.get('token')
    if not token: return abort(400)

    token_in_db = db.execute('SELECT * FROM tokens WHERE token = ?', (token,)).fetchone();
    if not token_in_db: return abort(401)

    response = make_response("")

    if datetime.now(timezone.utc) > datetime.strptime(token_in_db['valid_before'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc):
        new_token = secrets.token_urlsafe(24)

        db.execute("UPDATE tokens SET token = ?, valid_before = (SELECT datetime('now', '+1 month')) WHERE token = ?", (new_token, token))
        db.commit()

        response.set_cookie(key="token", value=new_token, max_age=60*60*24*365, secure=True)
        token = new_token

    if db.execute('SELECT * FROM votes WHERE token = ? AND post_id = ?', (token, id)).fetchone():
        db.execute('DELETE FROM votes WHERE token = ? AND post_id = ?;', (token, id))
        db.commit()
    else:
        db.execute('INSERT INTO votes (token, post_id) VALUES (?, ?);', (token, id))
        db.commit()

    response.headers['location'] = request.url
    return response, 302