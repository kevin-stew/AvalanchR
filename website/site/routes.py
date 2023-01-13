from flask import Blueprint, render_template
from flask_login import current_user
from website.models import User, Post, db
from config import Config

site = Blueprint('site', __name__, template_folder='site_templates')

@site.route('/')
def home():
    return render_template('index.html')


@site.route('/inventory')
def inventory():
    posts = Post.query.all()  #generates info for ALL posts in db
    posts.reverse() #reverses order of posts so most recent items show up first
    return render_template('inventory.html', posts=posts, Config=Config)


@site.route('/profile')
def profile():
    user_posts = Post.query.filter_by(user_id = current_user.id) #generates info for ALL posts in db
    # posts.reverse() #reverses order of posts so most recent items show up first
    return render_template('profile.html', user_posts = user_posts, Config = Config)


@site.route('/purchase/<id>', methods = ['GET'])
def purchase(id):
    # seller = Post.query.get(id)
    print(id)
    # seller = Post.query.filter(id=id)
    seller_id = Post.query.filter_by(id=id).first().user_id
    seller= User.query.filter_by(id=seller_id).first().email
    return render_template('purchase.html', seller=seller)


@site.route('/item/<id>', methods = ['GET'])
def item(id):
    post = Post.query.filter_by(id=id).first()
    return render_template('item.html', Config=Config, post=post)

