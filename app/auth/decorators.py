from functools import wraps

from flask import abort, redirect, url_for

from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        is_admin = getattr(current_user, 'is_admin', False)
        if not is_admin:
            abort(401)
        return f(*args, **kws)
    return decorated_function

def not_initial_status(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        if current_user.id_estado ==1:
            return redirect(url_for('auth.change_password'))
        return f(*args, **kws)
    return decorated_function