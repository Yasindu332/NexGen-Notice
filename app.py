from flask import Flask, request, render_template_string, redirect, url_for
import uuid

app = Flask(__name__)

# දත්ත තාවකාලිකව රඳවා තබා ගන්නා තැන (In-memory DB)
posts = {}

# --- HTML Templates ---

# 1. මුල් පිටුව (Create Post & List Posts)
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
        {% for post_id, post in posts.items() %}
            <li>
                <a href="/post/{{ post_id }}">{{ post.title }}</a> 
                - <a href="/edit/{{ post_id }}" style="color: green;">Edit</a> 
                - <a href="/delete/{{ post_id }}" style="color: red;">Delete</a>
            </li>
        {% endfor %}
    </ul>
</body>
</html>
'''

# 2. පොස්ට් එක බලන පිටුව (View Post)
VIEW_HTML = '''
<!DOCTYPE html>
<html>
<head><title>{{ post.title }}</title></head>
<body style="font-family: sans-serif; padding: 20px; max-width: 600px; margin: auto;">
    <h2>{{ post.title }}</h2>
    <p>{{ post.content }}</p>
    <br>
    <a href="/">ආපසු මුල් පිටුවට</a>
</body>
</html>
'''

# 3. පොස්ට් එක Update කරන පිටුව (Edit Post)
EDIT_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Edit Post</title></head>
<body style="font-family: sans-serif; padding: 20px; max-width: 600px; margin: auto;">
    <h2>පොස්ට් එක වෙනස් කරන්න (Edit)</h2>
    <form method="POST" action="/edit/{{ post_id }}">
        <input type="text" name="title" value="{{ post.title }}" required style="width: 100%; padding: 10px; margin-bottom: 10px;"><br>
        <textarea name="content" required rows="5" style="width: 100%; padding: 10px; margin-bottom: 10px;">{{ post.content }}</textarea><br>
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
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        # අලුත් ලින්ක් එකක් හදන්න Unique ID එකක් ගන්නවා
        post_id = str(uuid.uuid4())[:8] 
        posts[post_id] = {'title': title, 'content': content}
        return redirect(url_for('home'))
    
    return render_template_string(HOME_HTML, posts=posts)

@app.route('/post/<post_id>')
def view_post(post_id):
    post = posts.get(post_id)
    if post:
        return render_template_string(VIEW_HTML, post=post)
    return "Post not found!", 404

@app.route('/edit/<post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = posts.get(post_id)
    if not post:
        return "Post not found!", 404
        
    if request.method == 'POST':
        posts[post_id]['title'] = request.form['title']
        posts[post_id]['content'] = request.form['content']
        return redirect(url_for('home'))
        
    return render_template_string(EDIT_HTML, post=post, post_id=post_id)

@app.route('/delete/<post_id>')
def delete_post(post_id):
    if post_id in posts:
        del posts[post_id]
    return redirect(url_for('home'))

if __name__ == '__main__':
    # App එක රන් වෙන තැන
    app.run(debug=True)
