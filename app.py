"""Blogly application."""

from flask import Flask, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///blogly"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secretlysecret'

toolbar = DebugToolbarExtension(app)


connect_db(app)
db.create_all()


@app.route('/')
def root():
    return redirect("/users")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/users')
def users_index():


    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('users/index.html', users=users)


@app.route('/users/new', methods=["GET"])
def users_new_form():


    return render_template('users/new.html')


@app.route("/users/new", methods=["POST"])
def users_new():


    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form['image_url'] or None)

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>')
def users_show(user_id):


    user = User.query.get_or_404(user_id)
    return render_template('users/show.html', user=user)


@app.route('/users/<int:user_id>/edit')
def users_edit(user_id):


    user = User.query.get_or_404(user_id)
    return render_template('users/edit.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=["POST"])
def users_update(user_id):


    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def users_delete(user_id):

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>/posts/new')
def new_post_form(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('posts/new.html', user=user)

@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def new_post(user_id):
    user = User.query.get_or_404(user_id)
    new_p = Post(title=request.form['title'], content=request.form['content'], user=user)

    db.session.add(new_p)
    db.session.commit()
    flash(f"Post'{new_p.title}' added!")
    return redirect(f"/users/{user_id}")

@app.route('/posts/<int:post_id>')
def show_posts(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('posts/show.html', post=post)

@app.route('/posts/<int:post_id>/edit')
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('/posts/edit.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def update_posts(post_id):
    post=Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    db.session.add(post)
    db.session.commit()
    flash(f"Post '{post.title}' edited!")
    return redirect(f"/users/{post.user_id}")

@app.route('/posts/<int:post_id>/delete', methods={"POST"})
def delete_posts(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash(f"Post '{post.title}' has been deleted!")

    return redirect(f"/users/{post.user_id}")

@app.route('/tags')
def tags_index():
    tags = Tag.query.all()
    return render_template('tags/index.html', tags=tags)

@app.route('/tags/new')
def tags_new_form():
    posts= Post.query.all()
    return render_template('tags/new.html', posts=posts)

@app.route("/tags/new", methods=["POST"])
def tags_new():

    posts_ids = [int(num) for num in request.form.getlist("posts")]
    posts = Post.query.filter(Post.id.in_(posts_ids)).all()
    new_tag = Tag(name=request.form['name'], posts = posts)

    db.session.add(new_tag)
    db.session.commit()
    flash(f"Tag '{new_tag.name}' added.")

    return redirect("/tags")

@app.route('/tags/<int:tag_id>')
def tags_show(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags/show.html', tag=tag)

@app.route('/tags/<int:tag_id>/edit')
def tags_edit_form(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('tags/edit.html', tag=tag, posts=posts)

@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def tags_edit(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['name']
    post_ids = [int(num) for num in request.form.getlist("posts")]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    db.sesssion.add(tag)
    db.session.commit()

    flash(f"Tag '{tag.name}' editted!")
    return redirect("/tags")

@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def tags_delete(tag_id):

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.sesssion.commit()
    flash(f"Tag '{tag.name}' deleted!")

    return redirect("/tags")