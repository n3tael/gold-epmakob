from flask import Blueprint
import re

bp = Blueprint('template-utils', __name__)

@bp.app_template_filter()
def regex_replace(s, find, replace):
    """A non-optimal implementation of a regex filter"""
    return re.sub(find, replace, s)

@bp.app_template_filter()
def plural(n, first, second, third):
    if n % 10 == 1 and n % 100 != 11:
        return first
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return second
    else:
        return third