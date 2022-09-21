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
    id = db.Column(db.String, primary_key = True)
    first_name = db.Column(db.String(50), nullable = True, default='')
    last_name = db.Column(db.String(50), nullable = True, default = '')
    email = db.Column(db.String(100), nullable = False)
    password = db.Column(db.String, nullable = True, default = '')
    g_auth_verify = db.Column(db.Boolean, default = False)
    token = db.Column(db.String, default = '', unique = True )
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    post = db.relationship('Post', backref = "owner", lazy = True)  #allows post table to reference users

    def __init__(self, email, first_name = '', last_name = '', id = '', password = '', token = '', 
                  g_auth_verify = False):
        self.id = self.set_id()
        self.first_name = first_name
        self.last_name = last_name
        self.password = self.set_password(password)
        self.email = email
        self.token = self.set_token(24)
        self.g_auth_verify = g_auth_verify
    
    def give_info(self):
        user_info = {
            'email' : self.email,
            'first_name' : self.first_name,
            'token' : self.token 
        }
        return user_info
    
    def give_token(self):
        return self.token

    def set_id(self):
        return str(uuid.uuid4())

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)
        return self.pw_hash
    
    def set_token(self,length):
        return secrets.token_hex(length)

    def __repr__(self):
        return f'User {self.token} has been added to the database.'

# Post creation
class Post(db.Model):
    id = db.Column(db.String(50), primary_key = True)
    title = db.Column(db.String(50), nullable = True)
    description = db.Column(db.String(300), nullable = True)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable = False)
    dimensions = db.Column(db.String(100), nullable = True)
    weight = db.Column(db.String(50), nullable = True)
    img_url = db.Column(db.String, nullable = True )
    model_url = db.Column(db.String, nullable = True)
    user_token = db.Column(db.String, db.ForeignKey('user.token'), nullable = False)  #many drones can ONLY be assigend users
    

    def __init__(self, title, description, price, dimensions, weight, img_url, model_url, user_token, id=''):
        self.id = self.set_id()
        self.title = title
        self.description = description
        self.price = price
        self.dimensions = dimensions
        self.weight = weight
        self.img_url = img_url
        self.model_url = model_url
        self.user_token = user_token

    def set_id(self):
        return secrets.token_urlsafe()

    def __repr__(self):
        return f"{self.img_url}"


# Creation of API Schema via the Marshmallow Object
class PostSchema(ma.Schema):
    class Meta:
        fields = ['id', 
                  'title', 
                  'description', 
                  'price', 
                  'dimensions', 
                  'weight', 
                  'img_url', 
                  'model_url']

post_schema = PostSchema()
posts_schema = PostSchema(many=True)