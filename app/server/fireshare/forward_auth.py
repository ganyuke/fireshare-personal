"""Sign in from Caddy forward auth: Remote-User + X-Forward-Auth-Secret."""
import logging
from datetime import datetime

from flask import current_app, request
from flask_login import current_user, login_user

from . import db
from . import permissions as perms
from .models import User

logger = logging.getLogger('fireshare')


def try_forward_auth_login():
    secret = current_app.config.get('FORWARD_AUTH_SECRET') or ''
    if not secret or request.headers.get('X-Forward-Auth-Secret') != secret:
        return
    if current_user.is_authenticated:
        return

    raw_username = (request.headers.get('Remote-User') or '').strip()
    if not raw_username:
        return

    username = perms.normalize_username(raw_username)
    if not username:
        logger.warning('Forward auth: ignoring invalid Remote-User %r', raw_username)
        return

    user = User.query.filter(db.func.lower(User.username) == username.lower()).first()

    if not user:
        display_name = perms.clean_display_name(request.headers.get('Remote-Name'))
        user = User(
            username=username,
            password=None,
            admin=False,
            permissions=perms.serialize_permissions(list(perms.PRESETS['contributor'])),
            display_name=display_name,
            profile_public=True,
            created_at=datetime.utcnow(),
        )
        db.session.add(user)
        db.session.commit()
        logger.info('Forward auth: created user %r', username)

    if user.disabled:
        return

    login_user(user, remember=True)
    user.last_login_at = datetime.utcnow()
    db.session.commit()
