import io
import re
import sys
import sqlite3
import requests
from bs4 import BeautifulSoup
from PIL import Image

db = sqlite3.connect("instance/main.db")
cursor = db.cursor()

def parse(html):
    parsed_html = BeautifulSoup(html, 'lxml')

    if parsed_html.select_one('div.tgme_widget_message_error'):
        return {
            "fail": True,
            "reason": parsed_html.select_one('div.tgme_widget_message_error').get_text()
        }

    chat = parsed_html.select_one('.tgme_widget_message').get('data-post').split('/')[0]
    message_id = parsed_html.select_one('div.tgme_widget_message').get('data-post-id')

    author_name = parsed_html.select_one('.tgme_widget_message_author_name span').get_text()
    author_url = parsed_html.select_one('a.tgme_widget_message_author_name')
    if author_url:
        author_url = author_url.get('href')

    caption = parsed_html.select_one('div.tgme_widget_message_bubble .tgme_widget_message_text')
    if caption:
        caption = caption.get_text()

    created_at = parsed_html.select_one('time.datetime').get('datetime')

    images = []
    for photo in parsed_html.select('a.tgme_widget_message_photo_wrap'):
        # URL for photo looks like:
        # https://cdn0.cdn-telegram.org/file/sVZ6LPXXYTsPibNF9TpVT6La1NDd8LP7a1twG-gijUpGf4vd[...]_4S4Fdo3WgNMUdBMCxJy3InTvpoCHRyo428OIZR2dPgIXUKQ.jpg
        url = re.search(r"https:\/\/cdn[0-9].cdn-telegram.org\/file\/[a-zA-Z0-9_-]*.jpg", photo.get('style')).group()
        response = requests.get(url)

        # Convert to WEBP, for smaller size
        file = io.BytesIO()
        image = Image.open(io.BytesIO(response.content))
        image.save(file, 'webp', optimize = True, quality = 85)
        blob = file.getvalue()

        images.append(blob)

    return {
        "chat": chat,
        "message_id": message_id,
        "author": {
            "name": author_name,
            "url": author_url
        },
        "created_at": created_at,
        "caption": caption,
        "images": images
    }

def check_author(author):
    """
    Checks if the author is new and needs to be added to the database.
    Also updates the name or url if they have changed.

    Returns the author ID.
    """

    author_in_db = db.execute('SELECT * FROM authors WHERE name = ? AND url IS NOT NULL', (author['name'],)).fetchone()
    if author['url'] and not author_in_db:
        author_in_db = db.execute('SELECT * FROM authors WHERE url = ?', (author['url'],)).fetchone()
    else:
        author_in_db = db.execute('SELECT * FROM authors WHERE name = ?', (author['name'],)).fetchone()

    if not author_in_db:
        if not author['url']:
            cursor.execute('INSERT INTO authors (name) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM authors WHERE name = ?);', (author['name'], author['name']))
        else:
            cursor.execute('INSERT INTO authors (name, url) VALUES (?, ?)', (author['name'], author['url']))

        author_id = cursor.lastrowid
        db.commit()
        return author_id

    if author_in_db[1] != author['name']:
        cursor.execute('UPDATE authors SET name = ? WHERE url = ?', (author['name'], author['url']))
        db.commit()
        print(f'Updated author\'s name')

    if author_in_db[2] != author['url']:
        cursor.execute('UPDATE authors SET url = ? WHERE name = ?', (author['name'], author['name'])).fetchone()
        db.commit()
        print(f'Updated author\'s url')

    return author_in_db[0]

def add_message_to_db(message):
    author_id = check_author(message['author'])
    cursor.execute("INSERT INTO posts (chat, message_id, author_id, caption, created_at) VALUES (?, ?, ?, ?, ?)", (message['chat'], message['message_id'], author_id, message['caption'], message['created_at']))
    post_id = cursor.lastrowid
    db.commit()

    return post_id

def add_files_to_db(post_id, images):
    for image in images:
        cursor.execute("INSERT INTO images (post_id, image) VALUES (?, ?)", (post_id, image))
        db.commit()

def main():
    try:
        message_id_arg = sys.argv[1]
    except IndexError:
        message_id_arg = input('Link to message: ')

    url_match = re.search(r'https:\/\/t.me\/([a-zA-Z0-9_]*)\/(\d+)[^\d]*$', message_id_arg)

    if not url_match:
        print('fatal: failed to get id of message')
        sys.exit(1)

    group_username = url_match.group(1)
    message_id = url_match.group(2)

    print('Sending request to Telegram...')

    response = requests.get(f"https://t.me/{group_username}/{message_id}?embed=1")
    if response.status_code != 200:
        print('fatal: Telegram didn\'t respond status 200.')
        sys.exit(1)

    html_to_parse = response.text
    print('Parsing HTML...')
    message = parse(html_to_parse)
    if message.get('fail') == True:
        reason = message.get('reason')
        print(f'fatal: {reason}')
        sys.exit(1)

    print('Adding post to the database...')
    post_id = add_message_to_db(message)

    print('Adding images to the database...')
    add_files_to_db(post_id, message['images'])

    print('Done!')

if __name__ == "__main__":
    main()