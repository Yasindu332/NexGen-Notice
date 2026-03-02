from flask import Flask, request, render_template_string, redirect, url_for, g
import sqlite3
import uuid
import os

app = Flask(__name__)

# Vercel එකේ නම් /tmp ෆෝල්ඩර් එකේ සේව් කරන්න, නැත්නම් සාමාන්‍ය විදියට
if os.environ.get('VERCEL'):
    DATABASE = '/tmp/database.db'
else:
    DATABASE = 'database.db'

# --- Database Setup ---

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    db.commit()

# Vercel එකේ හැම රික්වෙස්ට් එකකටම කලින් Database Table එක තියෙනවද කියලා බලනවා
@app.before_request
def before_request():
    init_db()

# --- HTML Templates (with Modern CSS & JS) ---

HOME_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NegGen Solutions - Link Generator</title>
    <style>
        :root { --primary: #4f46e5; --primary-hover: #4338ca; --bg: #f3f4f6; --text: #1f2937; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--bg); color: var(--text); margin: 0; padding: 0; }
        .navbar { background: white; padding: 1rem 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;}
        .navbar h1 { margin: 0; font-size: 1.5rem; color: var(--primary); font-weight: bold; }
        .navbar a { text-decoration: none; color: inherit; }
        .container { max-width: 800px; margin: 0 auto; padding: 0 1rem; }
        .card { background: white; border-radius: 0.5rem; padding: 2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .form-group { margin-bottom: 1.5rem; }
        label { font-weight: 600; margin-bottom: 0.5rem; display: block; color: #4b5563; }
        input, textarea { width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; font-size: 1rem; box-sizing: border-box;}
        input:focus, textarea:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2); }
        .btn { display: inline-block; background: var(--primary); color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 0.375rem; font-size: 1rem; font-weight: 600; cursor: pointer; transition: background 0.2s; text-decoration: none;}
        .btn:hover { background: var(--primary-hover); }
        .btn-sm { padding: 0.5rem 1rem; font-size: 0.875rem; }
        .btn-outline { background: transparent; color: var(--primary); border: 1px solid var(--primary); }
        .btn-outline:hover { background: var(--primary); color: white; }
        .btn-danger { background: #ef4444; border: 1px solid #ef4444; color: white;}
        .btn-danger:hover { background: #dc2626; border-color: #dc2626;}
        .btn-edit { background: #10b981; border: 1px solid #10b981; color: white;}
        .btn-edit:hover { background: #059669; border-color: #059669;}
        .post-list { list-style: none; padding: 0; }
        .post-item { background: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;}
        .post-title { font-size: 1.25rem; font-weight: 600; margin: 0; color: var(--text); }
        .post-actions { display: flex; gap: 0.5rem; flex-wrap: wrap;}
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/"><h1>NegGen Solutions</h1></a>
    </nav>
    <div class="container">
        <div class="card">
            <h2 style="margin-top: 0; margin-bottom: 1.5rem;">Create New Link</h2>
            <form method="POST" action="/">
                <div class="form-group">
                    <label>Title</label>
                    <input type="text" name="title" placeholder="Enter title" required>
                </div>
                <div class="form-group">
                    <label>Text Content</label>
                    <textarea name="content" placeholder="Type your text here..." required rows="5"></textarea>
                </div>
                <button type="submit" class="btn">Generate Link</button>
            </form>
        </div>

        <h3 style="margin-bottom: 1rem;">Generated Links</h3>
        <ul class="post-list">
            {% for post in posts %}
                <li class="post-item">
                    <h4 class="post-title">{{ post['title'] }}</h4>
                    <div class="post-actions">
                        <button onclick="copyLink('{{ post['id'] }}')" class="btn btn-outline btn-sm">Copy Link</button>
                        <a href="/post/{{ post['id'] }}" class="btn btn-outline btn-sm" target="_blank">View</a>
                        <a href="/edit/{{ post['id'] }}" class="btn btn-edit btn-sm">Edit</a>
                        <a href="/delete/{{ post['id'] }}" class="btn btn-danger btn-sm" onclick="return confirm('Are you sure you want to delete this?')">Delete</a>
                    </div>
                </li>
            {% else %}
                <p style="color: #6b7280; text-align: center; margin-top: 2rem;">No links have been generated yet.</p>
            {% endfor %}
        </ul>
    </div>

    <script>
        function copyLink(postId) {
            const url = window.location.origin + "/post/" + postId;
            navigator.clipboard.writeText(url).then(() => {
                alert("Link copied to clipboard successfully!");
            }).catch(err => {
                console.error('Failed to copy: ', err);
                alert("Failed to copy link.");
            });
        }
    </script>
</body>
</html>
'''

VIEW_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ post['title'] }}</title>
    <style>
        :root { --primary: #4f46e5; --bg: #f3f4f6; --text: #1f2937; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--bg); color: var(--text); margin: 0; padding: 0; }
        .navbar { background: white; padding: 1rem 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .navbar h1 { margin: 0; font-size: 1.5rem; color: var(--primary); font-weight: bold; }
        .navbar a { text-decoration: none; color: inherit; }
        .container { max-width: 800px; margin: 0 auto; padding: 0 1rem; }
        .card { background: white; border-radius: 0.5rem; padding: 3rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        h1.title { font-size: 2.5rem; margin-top: 0; margin-bottom: 1.5rem; color: var(--text); border-bottom: 2px solid #e5e7eb; padding-bottom: 1rem;}
        p.content { font-size: 1.125rem; line-height: 1.8; color: #4b5563; white-space: pre-wrap; margin-bottom: 0;}
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/"><h1>NegGen Solutions</h1></a>
    </nav>
    <div class="container">
        <div class="card">
            <h1 class="title">{{ post['title'] }}</h1>
            <p class="content">{{ post['content'] }}</p>
        </div>
    </div>
</body>
</html>
'''

EDIT_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Link - {{ post['title'] }}</title>
    <style>
        :root { --primary: #4f46e5; --bg: #f3f4f6; --text: #1f2937; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--bg); color: var(--text); margin: 0; padding: 0; }
        .navbar { background: white; padding: 1rem 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .navbar h1 { margin: 0; font-size: 1.5rem; color: var(--primary); font-weight: bold; }
        .navbar a { text-decoration: none; color: inherit; }
        .container { max-width: 800px; margin: 0 auto; padding: 0 1rem; }
        .card { background: white; border-radius: 0.5rem; padding: 2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 1.5rem; }
        label { font-weight: 600; margin-bottom: 0.5rem; display: block; color: #4b5563; }
        input, textarea { width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; font-size: 1rem; box-sizing: border-box;}
        input:focus, textarea:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2); }
        .btn { display: inline-block; background: #10b981; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 0.375rem; font-size: 1rem; font-weight: 600; cursor: pointer; transition: background 0.2s;}
        .btn:hover { background: #059669; }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/"><h1>NegGen Solutions</h1></a>
    </nav>
    <div class="container">
        <div class="card">
            <h2 style="margin-top: 0; margin-bottom: 1.5rem;">Edit Content</h2>
            <form method="POST" action="/edit/{{ post['id'] }}">
                <div class="form-group">
                    <label>Title</label>
                    <input type="text" name="title" value="{{ post['title'] }}" required>
                </div>
                <div class="form-group">
                    <label>Text Content</label>
                    <textarea name="content" required rows="8">{{ post['content'] }}</textarea>
                </div>
                <button type="submit" class="btn">Update Information</button>
            </form>
        </div>
    </div>
</body>
</html>
'''

# --- Routes (Backend Logic) ---

@app.route('/', methods=['GET', 'POST'])
def home():
    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post_id = str(uuid.uuid4())[:8] 
        db.execute('INSERT INTO posts (id, title, content) VALUES (?, ?, ?)', (post_id, title, content))
        db.commit()
        return redirect(url_for('home'))
    
    posts = db.execute('SELECT * FROM posts').fetchall()
    return render_template_string(HOME_HTML, posts=posts)

@app.route('/post/<post_id>')
def view_post(post_id):
    post = get_db().execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    if post:
        return render_template_string(VIEW_HTML, post=post)
    return "Post not found!", 404

@app.route('/edit/<post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    if not post:
        return "Post not found!", 404
        
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        db.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, post_id))
        db.commit()
        return redirect(url_for('home'))
        
    return render_template_string(EDIT_HTML, post=post)

@app.route('/delete/<post_id>')
def delete_post(post_id):
    db = get_db()
    db.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    db.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        init_db() 
    app.run(debug=True)
