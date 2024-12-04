from uuid import uuid4
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS screenshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            language TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS IgnoreRegions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            screenshot_id INTEGER,
            description TEXT,
            x INTEGER,
            y INTEGER,
            width INTEGER,
            height INTEGER,
            FOREIGN KEY(screenshot_id) REFERENCES screenshots(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS OperatingSystems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_num INTEGER NOT NULL UNIQUE
        )
    ''')
    initial_data = [(13,), (14,), (15,)]
    c.executemany('INSERT OR IGNORE INTO OperatingSystems (version_num) VALUES (?)', initial_data)
    c.execute('''
        CREATE TABLE IF NOT EXISTS ScreenshotOperatingSystem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            screenshot_id INTEGER,
            os_id INTEGER,
            FOREIGN KEY(screenshot_id) REFERENCES screenshots(id),
            FOREIGN KEY(os_id) REFERENCES OperatingSystems(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def show_screenshots():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM screenshots')
    rows = c.fetchall()
    conn.close()

    # Convert rows to list of dictionaries
    screenshots = []
    for row in rows:
        screenshots.append({
            'id': row[0],
            'filename': row[1],
            'filepath': row[2],
            'language': row[3]
        })

    return render_template('screenshots.html', screenshots=screenshots)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        language = request.form['language']
        file = request.files['file']
        os_versions = request.form.getlist('os_versions')

        if file:
            uuid = str(uuid4())
            ext = file.filename.split('.')[-1]
            filename = file.filename
            filepath = f'uploads/{uuid}.{ext}'
            file.save(filepath)

            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute('INSERT INTO screenshots (filename, filepath, language) VALUES (?, ?, ?)', (filename, filepath, language))
            screenshot_id = c.lastrowid

            for os_id in os_versions:
                c.execute('INSERT INTO ScreenshotOperatingSystem (screenshot_id, os_id) VALUES (?, ?)', (screenshot_id, os_id))

            conn.commit()
            conn.close()

            return redirect(url_for('upload_file', success=True))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM OperatingSystems')
    operating_systems = c.fetchall()
    operating_systems = [
        { 
            'id': ver[0],
            'version_num': ver[1]
        }
        for ver in operating_systems
    ]
    conn.close()

    return render_template('upload.html', operating_systems=operating_systems)

@app.route('/screenshot/<int:id>')
def screenshot_detail(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM screenshots WHERE id = ?', (id,))
    row = c.fetchone()
    screenshot = {
        'id': row[0],
        'filename': row[1],
        'filepath': row[2],
        'actual_filename': row[2].split('/')[-1],
        'language': row[3]
    }

    c.execute('SELECT * FROM IgnoreRegions WHERE screenshot_id = ?', (id,))
    ignore_regions = c.fetchall()
    ignore_regions = [
        {
            'id': region[0],
            'description': region[2],
            'x': region[3],
            'y': region[4],
            'width': region[5],
            'height': region[6]
        }
        for region in ignore_regions
    ]
    c.execute('SELECT * FROM OperatingSystems WHERE id IN (SELECT os_id FROM ScreenshotOperatingSystem WHERE screenshot_id = ?)', (id,))
    supported_operating_systems = c.fetchall()
    supported_operating_systems = [
        {
            'id': os[0],
            'version_num': os[1]
        }
        for os in supported_operating_systems
    ]
    conn.close()
    return render_template('detail.html', screenshot=screenshot, ignore_regions=ignore_regions, supported_operating_systems=supported_operating_systems)

@app.route('/screenshot/<int:id>/add_ignore_region', methods=['POST'])
def add_ignore_region(id):
    description = request.form.get('description')
    x = request.form.get('x')
    y = request.form.get('y')
    width = request.form.get('width')
    height = request.form.get('height')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO IgnoreRegions (screenshot_id, description, x, y, width, height)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (id, description, x, y, width, height))
    conn.commit()
    conn.close()

    return redirect(url_for('screenshot_detail', id=id))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
