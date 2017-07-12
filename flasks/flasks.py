import sqlite3
from flask import Flask, url_for, request, session, abort, redirect, g, render_template, flash

app = Flask(__name__)
app.config.from_pyfile('E:\\flasks\\instance\\config.py')

def initdb():
    db = get_db()
    with app.open_resource('schema.sql', 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    initdb()
    print('initializing the database')

def connect_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.cursor().execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You have logged in.')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have logged out')
    return redirect(url_for('show_entries'))

@app.route('/add', methods=['POST'])
def add_entries():
    if not session['logged_in']:
        abort(401)
    db = get_db()
    db.execute('insert into entries(title, text) values(?, ?)', [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()

