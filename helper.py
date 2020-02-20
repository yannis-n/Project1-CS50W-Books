from functools import wraps
import os

import urllib.parse

from flask import redirect, render_template, request, session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def decimal_c(value):
    """Format value as USD."""
    return f"{value:,.2f}"
