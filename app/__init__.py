import os
import logging
from flask import Flask
from flask_wtf import CSRFProtect
from flask_squeeze import Squeeze
from flask_minify import Minify

squeeze = Squeeze()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import config
    app.config.from_object(config.Config(app.instance_path))

    handler = logging.FileHandler('error.log')
    app.logger = logging.getLogger(__name__)
    app.logger.setLevel(logging.ERROR)
    app.logger.addHandler(handler)

    from . import db
    db.init_app(app)

    squeeze.init_app(app)
    Minify(app=app, html=True, js=True, cssless=True)

    csrf.init_app(app)

    from . import template_utils
    app.register_blueprint(template_utils.bp)

    from . import errors
    app.register_blueprint(errors.bp)

    from . import index
    app.register_blueprint(index.bp)

    from . import images
    app.register_blueprint(images.bp)

    from . import authors
    app.register_blueprint(authors.bp)

    from . import posts
    app.register_blueprint(posts.bp)

    return app