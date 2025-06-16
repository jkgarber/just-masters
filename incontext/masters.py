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
    list_masters = get_user_masters('list')
    agent_masters = get_user_masters('agent')
    return render_template('masters/index.html', list_masters=list_masters, agent_masters=agent_masters)


@bp.route('/new/<master_type>', methods=('GET', 'POST'))
@login_required
def new(master_type):
    if master_type not in ['list', 'agent']:
        abort(404)
    if request.method == 'POST':
        if master_type == 'list':
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
                    'INSERT INTO masters (name, master_type, description, creator_id)'
                    ' VALUES (?, ?, ?, ?)',
                    (name, master_type, description, g.user['id'])
                )
                db.commit()
                return redirect(url_for('masters.index'))
        elif master_type == 'agent':
            abort(404) # TODO

    return render_template('masters/new.html', master_type=master_type)


@bp.route('/<int:master_id>/view')
@login_required
def view(master_id):
    master = get_master(master_id)
    print(master)
    if master['master_type'] == 'list':
        return render_template('masters/view.html', master=master)
    elif master['master_type'] == 'agent':
        abort(404) # TODO
    else:
        abort(404)


@bp.route('/<int:master_id>/edit', methods=('GET', 'POST'))
@login_required
def edit(master_id):
    master = get_master(master_id)
    if request.method == "POST":
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
                'UPDATE masters SET name = ?, description = ?'
                ' WHERE id = ?',
                (name, description, master_id)
            )
            db.commit()
            return redirect(url_for('masters.index'))
    return render_template("masters/edit.html", master=master)


@bp.route("<int:master_id>/delete", methods=("POST",))
@login_required
def delete(master_id):
    master = get_master(master_id)
    return "TODO", 200


@bp.route('<int:master_id>/items/new', methods=("GET", "POST"))
@login_required
def new_item(master_id):
    master = get_master(master_id)
    if request.method == "POST":
        name = request.form['name']
        detail_fields = []
        details = [detail for detail in master['details']]
        for detail in details:
            detail_id = detail['id']
            detail_content = request.form[str(detail_id)]
            detail_fields.append((detail_id, detail_content))
        error = None
        if not name:
            error = 'Name is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            cur = db.cursor()
            cur.execute(
                'INSERT INTO master_items (name, creator_id)'
                ' VALUES (?, ?)',
                (name, g.user['id'])
            )
            item_id = cur.lastrowid
            cur.execute(
                'INSERT INTO master_item_relations (master_id, master_item_id)'
                ' VALUES (?, ?)',
                (master_id, item_id)
            )
            relations = []
            for field in detail_fields:
                relations.append((item_id,) + field)
            cur.executemany(
                'INSERT INTO master_item_detail_relations (master_item_id, master_detail_id, content)'
                ' VALUES(?, ?, ?)',
                relations
            )
            db.commit()
            return redirect(url_for('masters.view', master_id=master_id))
    return render_template("masters/items/new.html", master=master)


@bp.route("<int:master_id>/items/<int:item_id>/view")
@login_required
def view_item(master_id, item_id):
    master = get_master(master_id)
    requested_item = None
    for item in master['items']:
        if item['id'] == item_id:
            requested_item = item
    return render_template("masters/items/view.html", item=requested_item, details=master["details"])


@bp.route("<int:master_id>/items/<int:item_id>/edit", methods=("GET", "POST"))
@login_required
def edit_item(master_id, item_id):
    master = get_master(master_id)
    requested_item = None
    for item in master["items"]:
        if item["id"] == item_id:
            requested_item = item
    if request.method == "POST":
        return "", 200
    return render_template("masters/items/edit.html", master=master, item=requested_item)


def get_user_masters(master_type):
    db = get_db()
    user_masters = db.execute(
        'SELECT m.id, m.name, m.master_type, m.description, m.created'
        ' FROM masters m'
        ' WHERE m.creator_id = ?'
        ' AND m.master_type = ?',
        (g.user['id'], master_type)
    ).fetchall()
    return user_masters


def get_master(master_id, check_access=True):
    db = get_db()
    master = db.execute(
        'SELECT m.id, m.creator_id, m.created, m.master_type, m.name, m.description'
        ' FROM masters m'
        ' WHERE m.id = ?',
        (master_id,)
    ).fetchone()
    if master is None:
        abort(404)
    if check_access:
        if master['creator_id'] != g.user['id']:
            abort(403)
    if master['master_type'] == 'list':
        list_master = {}
        for key in master.keys():
            list_master[key] = master[key]
        items = db.execute(
            'SELECT i.id, i.name, i.created'
            ' FROM master_items i'
            ' JOIN master_item_relations m'
            ' ON m.master_item_id = i.id'
            ' WHERE m.master_id = ?',
            (master_id,)
        ).fetchall()
        list_master['items'] = []
        for item in items:
            new_item = {}
            for key in item.keys():
                new_item[key] = item[key]
            new_item['contents'] = []
            item_id = str(item['id'])
            # list_master['items'][item_id] = new_item
            list_master['items'].append(new_item)
        details = db.execute(
            'SELECT d.id, d.name, d.description'
            ' FROM master_details d'
            ' JOIN master_detail_relations m'
            ' ON m.master_detail_id = d.id'
            ' WHERE m.master_id = ?',
            (master_id,)
        ).fetchall()
        list_master['details'] = details
        contents = db.execute(
            'SELECT master_item_id, content'
            ' FROM master_item_detail_relations'
            ' WHERE master_detail_id IN'
            ' (SELECT master_detail_id'
            '  FROM master_detail_relations'
            '  WHERE master_id = ?)',
            (master_id,)
        ).fetchall()
        for content in contents:
            item_id = content['master_item_id']
            list_master['items'][item_id]['contents'].append(content['content'])
        return list_master
