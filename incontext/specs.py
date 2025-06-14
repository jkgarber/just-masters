from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from incontext.auth import login_required
from incontext.db import get_db

bp = Blueprint('specs', __name__, url_prefix='/specs')

@bp.route('/')
@login_required
def index():
    specs = get_user_specs()
    return render_template('specs/index.html', specs=specs)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        error = None
        if not name:
            error = 'Name is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO specs (name, description, creator_id)'
                ' VALUES (?, ?, ?)',
                (name, description, g.user['id'])
            )
            db.commit()
            return redirect(url_for('specs.index'))

    return render_template('specs/create.html')


def get_user_specs():
    db = get_db()
    user_specs = db.execute(
        'SELECT s.id, s.name, s.description, s.created'
        ' FROM specs s'
        ' WHERE s.creator_id = ?',
        (g.user['id'],)
    ).fetchall()
    return user_specs


