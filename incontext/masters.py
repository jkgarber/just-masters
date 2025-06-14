from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from incontext.auth import login_required
from incontext.db import get_db

bp = Blueprint('masters', __name__, url_prefix='/masters')

@bp.route('/')
@login_required
def index():
    list_masters = get_user_masters('List')
    agent_masters = get_user_masters('Agent')
    return render_template('masters/index.html', list_masters=list_masters, agent_masters=agent_masters)


@bp.route('/new', methods=('GET', 'POST'))
@login_required
def new():
    if request.method == 'POST':
        name = request.form['name']
        master_type = request.form['master_type']
        description = request.form['description']
        error = None
        if not name:
            error = 'Name is required.'
        if not master_type:
            error = 'Type is required.'
        if master_type not in ['List', 'Agent']:
            error = 'Invalid master type.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO masters (name, master_type, description, creator_id)'
                ' VALUES (?, ?, ?, ?)',
                (name, master_type, description, g.user['id'])
            )
            db.commit()
            return redirect(url_for('masters.index'))

    return render_template('masters/new.html')


@bp.route('/<int:master_id>/view')
@login_required
def view(master_id):
    master = get_master(master_id)
    return '', 200


@bp.route('/<int:master_id>/edit')
@login_required
def edit(master_id):
    master = get_master(master_id)
    return '', 200


def get_user_masters(master_type):
    db = get_db()
    user_masters = db.execute(
        'SELECT m.id, m.name, m.master_type, m.description, m.enabled, m.created'
        ' FROM masters m'
        ' WHERE m.creator_id = ?'
        ' AND m.master_type = ?',
        (g.user['id'], master_type)
    ).fetchall()
    return user_masters


