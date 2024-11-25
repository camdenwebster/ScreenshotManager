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
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
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
        return 'File uploaded and saved to database'
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
