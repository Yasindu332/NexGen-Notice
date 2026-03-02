from flask import Flask, request, render_template_string, redirect, url_for, g
import sqlite3
import uuid

app = Flask(__name__)
DATABASE = 'database.db'

# --- Database Setup ---

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row # දත්ත Dictionary එකක් වගේ ගන්න
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Table එක මුලින්ම හදාගන්න කොටස
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        ''')
        db.commit()

# --- HTML Templates ---

HOME_HTML = '''
<!DOCTYPE html>
<html>
<head><title>NegGen Solutions - Posts</title></head>
<body style="font-family: sans-serif; padding: 20px; max-width: 600px; margin: auto;">
    <h2>අලුත් පොස්ට් එකක් හදන්න</h2>
    <form method="POST" action="/">
        <input type="text" name="title" placeholder="මාතෘකාව" required style="width: 100%; padding: 10px; margin-bottom: 10px;"><br>
        <textarea name="content" placeholder="විස්තරය" required rows="5" style="width: 100%; padding: 10px; margin-bottom: 10px;"></textarea><br>
        <button type="submit" style="padding: 10px 15px; background: #007BFF; color: white; border: none; cursor: pointer;">Create Link</button>
    </form>
    
    <hr>
    <h3>හැදුව පොස්ට් (Posts)</h3>
    <ul>
        {% for post in posts %}
            <li>
                <a href="/post/{{ post['id'] }}">{{ post['title'] }}</a> 
                - <a href="/edit/{{ post['id'] }}" style="color: green;">Edit</a> 
                - <a href="/delete/{{ post['id'] }}" style="color: red;">Delete</a>
            </li>
        {% endfor %}
    </ul>
</body>
</html>
'''

VIEW_HTML = '''
<!DOCTYPE html>
<html>
<head><title>{{ post['title'] }}</title></head>
<body style="font-family: sans-serif; padding: 20px; max-width: 600px; margin: auto;">
    <h2>{{ post['title'] }}</h2>
    <p>{{ post['content'] }}</p>
    <br>
    <a href="/">ආපසු මුල් පිටුවට</a>
</body>
</html>
'''

EDIT_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Edit Post</title></head>
<body style="font-family: sans-serif; padding: 20px; max-width: 600px; margin: auto;">
    <h2>පොස්ට් එක වෙනස් කරන්න (Edit)</h2>
    <form method="POST" action="/edit/{{ post['id'] }}">
        <input type="text" name="title" value="{{ post['title'] }}" required style="width: 100%; padding: 10px; margin-bottom: 10px;"><br>
        <textarea name="content" required rows="5" style="width: 100%; padding: 10px; margin-bottom: 10px;">{{ post['content'] }}</textarea><br>
        <button type="submit" style="padding: 10px 15px; background: #28a745; color: white; border: none; cursor: pointer;">Update</button>
    </form>
    <br>
    <a href="/">ආපසු මුල් පිටුවට</a>
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
        
        # දත්ත Database එකට ඇතුලත් කිරීම
        db.execute('INSERT INTO posts (id, title, content) VALUES (?, ?, ?)', (post_id, title, content))
        db.commit()
        return redirect(url_for('home'))
    
    # Database එකෙන් දත්ත ගැනීම
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
        # Database එකේ දත්ත Update කිරීම
        db.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, post_id))
        db.commit()
        return redirect(url_for('home'))
        
    return render_template_string(EDIT_HTML, post=post)

@app.route('/delete/<post_id>')
def delete_post(post_id):
    db = get_db()
    # Database එකෙන් දත්ත Delete කිරීම
    db.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    db.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db() # App එක රන් වෙද්දි මුලින්ම Database එක හදනවා
    app.run(debug=True)
