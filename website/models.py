import uuid
from datetime import datetime
import secrets

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_marshmallow import Marshmallow

# Adding Flask Security for Passwords
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
login_manager = LoginManager()
ma = Marshmallow()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(50), nullable = True, default='')
    last_name = db.Column(db.String(50), nullable = True, default = '')
    email = db.Column(db.String(100), nullable = False)
    password = db.Column(db.String, nullable = True, default = '')
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    post = db.relationship('Post', backref = "owner", lazy = True)  # allows post table to reference users

    def __init__(self, email, first_name = '', last_name = '', id = '', password = ''):
        self.id = None
        self.first_name = first_name
        self.last_name = last_name
        self.password = self.set_password(password)
        self.email = email

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)
        return self.pw_hash

    def __repr__(self):
        return f'User {self.email} (#{self.id}) has been added to the database.'

# Post creation
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50), nullable = True)
    description = db.Column(db.String(300), nullable = True)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable = False)
    dimensions = db.Column(db.String(50), nullable = True)
    weight = db.Column(db.String(50), nullable = True)
    # img_url = db.Column(db.String, nullable = True )
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

    model_url = db.Column(db.String, nullable = True)
    glb = db.Column(db.String, nullable = True)
    stl = db.Column(db.String, nullable = True)
    obj = db.Column(db.String, nullable = True)
    studio_max = db.Column(db.String, nullable = True)
    dae = db.Column(db.String, nullable = True)
    skp = db.Column(db.String, nullable = True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)  # many users can ONLY be assigend one user

    def __init__(self, title, description, price, dimensions, weight, \
                model_url, glb, stl, obj, studio_max, dae, skp, \
                user_id, id=''):

        self.id = None
        self.title = title
        self.description = description
        self.price = price
        self.dimensions = dimensions
        self.weight = weight
        # self.img_url = img_url
        
        self.model_url = model_url
        self.glb = glb
        self.stl = stl
        self.obj = obj
        self.studio_max = studio_max
        self.dae = dae
        self.skp = skp

        self.user_id = user_id

    def __repr__(self):
        return f"{self.model_url}"

# Creation of API Schema via the Marshmallow Object
class PostSchema(ma.Schema):
    class Meta:
        fields = ['id', 
                  'title', 
                  'description', 
                  'price', 
                  'dimensions', 
                  'weight', 
                  'date_created', 
                  'model_url']

post_schema = PostSchema()
posts_schema = PostSchema(many=True)



# ---------SEPERATE TABLE JUST FOR 3D FILES--------------
# class File_3D(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key = True)
#     glb = db.Column(db.String, nullable = True)
#     stl = db.Column(db.String, nullable = True)
#     obj = db.Column(db.String, nullable = True)
#     studio_max = db.Column(db.String, nullable = True)
#     dae = db.Column(db.String, nullable = True)
#     skp = db.Column(db.String, nullable = True)
#     post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable = False)  # many model files can ONLY be assigend one post
    
#     def __init__(self, glb, stl, obj, studio_max, dae, skp, post_id, id=''):
#         self.id = None
#         self.glb = glb
#         self.stl = stl
#         self.obj = obj
#         self.studio_max = studio_max
#         self.dae = dae
#         self.skp = skp
#         self.post_id = post_id

#     def __repr__(self):
#         return f"mode table #{self.id} is now made"
# ---------SEPERATE TABLE JUST FOR 3D FILES--------------