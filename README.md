# gold-epmakob

![gold-epmakob](assets/logo.webp)

**gold-epmakob** («Золотая галерея Ермакова») is a web-gallery written in Python. Images are taken from the public chats in Telegram, which are manually added by the administrator.

## No JavaScript, no ads, no trackers

But if JavaScript not enabled, some features will be missing:

- Auto-load next page in all posts.
- Copy button on the post page.

## Getting started

### Running

1. Install [PyPy3](https://www.pypy.org/download.html).
2. Create virtual environment: `pypy3 -m venv env`.
3. Activate virtual environment:

   On Linux: `source env/bin/activate`.

   On Windows: `env\Scripts\activate`.
4. Install requirements: `pip3 install -r requirements.txt`.
5. Initialize the Database File: `flask --app app init-db`.
6. Change app configuration in `./app/config.py`.
7. Change footer text in `./app/templates/footer.html`.
8. Run the app `pypy3 run`.

### Utilities

> [!IMPORTANT]
> All scripts require an [initialized database](#running).

#### Add posts

1. Run script: `pypy3 utils/add-post.py`
2. Enter link to message.
3. Post added!

#### Clear expired tokens

1. Run script: `pypy3 utils/add-post.py`
2. Expired tokens cleared.

## Development server

Run: `flask --app app run --debug`
