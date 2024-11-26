from flask import Flask, request, redirect, url_for, render_template
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
        language = request.form.get('language')
        if not language:
            return 'No language selected'
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if not file or not file.filename:
            return 'No selected file'
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Save to database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO screenshots (filename, filepath, language) VALUES (?, ?, ?)', (filename, filepath, language))
        conn.commit()
        conn.close()
        return redirect(url_for('upload_file', success=True))
    return render_template('upload.html')

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

    conn.close()
    return render_template('detail.html', screenshot=screenshot, ignore_regions=ignore_regions)

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

if __name__ == '__main__':
    app.run(debug=True)
