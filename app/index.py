from flask import Blueprint, render_template, request
from app.db import get_db

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    db = get_db()

    best_posts = db.execute('SELECT * FROM all_posts ORDER BY total_votes DESC LIMIT 5').fetchall()
    latest_posts = db.execute('SELECT * FROM all_posts ORDER BY uploaded_at DESC LIMIT 5').fetchall()

    stats_raw = db.execute('''SELECT (SELECT count(*) from authors) AS total_authors,
	                                 (SELECT count(*) from posts) AS total_posts,
	                                 (SELECT count(*) from votes) AS total_votes''').fetchone()

    stats = {
        "total_authors": stats_raw['total_authors'],
        "total_posts": stats_raw['total_posts'],
        "total_votes": stats_raw['total_votes'],
    }

    return render_template('index.html', best_posts=best_posts, latest_posts=latest_posts, stats=stats)