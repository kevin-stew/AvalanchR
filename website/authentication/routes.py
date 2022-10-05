from flask import Blueprint, flash, render_template, request, redirect, url_for, send_from_directory, abort
from flask_login import login_user, logout_user, current_user, login_required
import boto3, os

# project file imports
from website.forms import UserLoginForm, ObjectUploadForm, UserSignupForm
from website.models import User, Post, db, check_password_hash, post_schema, posts_schema
from config import Config

#from file upload tutorial for images and files
import os, ntpath
from werkzeug.utils import secure_filename

auth = Blueprint('auth', __name__, template_folder ='auth_templates')

#----------------------SIGN_UP--------------------------
@auth.route('/signup', methods = ['GET','POST'])
def signup():
    form = UserSignupForm()

    try:
        if request.method == 'POST' and form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            print(email,password)

            # Add User into Database
            test = User.query.filter(User.email == email).first()
            if email == test:
                print(email, 'already in db')
                flash(f'{email} already has an account with us.','auth-failed')
                return redirect(url_for('auth.login'))
            else:
                user = User(email,password = password)
                db.session.add(user)
                db.session.commit()
                flash(f'You have successfully created a user account for {email}.', "user-created")
                
                #login new user & redirect to inventory page
                logged_user = User.query.filter(User.email == email).first()
                login_user(logged_user)
                
                return redirect(url_for('site.profile'))
    except:
        raise Exception('Invalid Form Data: Please check your form.')

    return render_template('signup.html', form=form)

#----------------------LOG_IN--------------------------
@auth.route('/login', methods = ['GET', 'POST'])
def login():
    form = UserLoginForm()

    try:
        if request.method == 'POST' and form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            print(email, password)

            #---------Query user table for users with this info----------------
            logged_user = User.query.filter(User.email == email).first()

            #----------Check if logged_user and password == password--------------
            if logged_user and check_password_hash(logged_user.password, password):
                login_user(logged_user)
                flash('You were successfully logged in', 'auth-success')
                return redirect(url_for('site.profile'))
            else:
                flash('Your Email/Password is incorrect.', 'auth-failed')
                return redirect(url_for('auth.login'))

    except:
        raise Exception('Invalid Form Data: Please check your form.')

    return render_template('login.html', form=form)

#-----------EXCEED UPLOAD SIZE MAX-----------------
# @auth.errorhandler(400)
# def image_too_large(error):
#     error=['Image file is too large', 'Oops']
#     return render_template('413.html'), 413

#----------------------UPLOAD_FORM--------------------------
@auth.route('/upload', methods = ['GET', 'POST'])
@login_required
def upload():
    form = ObjectUploadForm()
    # try:

    if request.method == 'POST':

        #check image existance / extension before processing db update:
        if not request.files["image"]:
            flash('⚠ Please attach a preview image file')
            return render_template('upload.html', form=form)
        else:
            uploadimage = request.files["image"].filename
            image_ext = os.path.splitext(uploadimage)[1].lower()
            if image_ext not in Config.ALLOWED_IMAGES:
                flash('⚠ Image extension not allowed')
                return render_template('upload.html', form=form)

        #check model existance / extension before processing db update:
        if not request.files["model"]:
            flash('⚠ Please attach a 3D model file')
            return render_template('upload.html', form=form)
        else:
            uploadmodel = request.files["model"].filename
            model_ext = os.path.splitext(uploadmodel)[1].lower()
            if model_ext not in Config.ALLOWED_MODELS:
                flash('⚠ Model extension not allowed')
                return render_template('upload.html', form=form)

        # --------- size tests -------------
        image_test = request.files["image"]
        
        print('--', image_test.content_length)
        print('**', image_test.tell())
        print('****', image_test.seek(0, os.SEEK_SET))
        
        # --------- size tests -------------
        
        # load db variables here
        title = form.title.data
        description = form.description.data
        price = form.price.data
        dimensions = form.dimensions.data
        weight = form.weight.data
        img_url = upload_image()
        model_url = upload_model() 
        user_id = current_user.id

        print(title, description, price, dimensions, weight, img_url, model_url)

        post = Post(title, description, price, dimensions, weight, img_url, model_url, user_id)

        db.session.add(post)
        db.session.commit()    
         
            
        return redirect(url_for('site.profile'))

        # return redirect(url_for('auth.upload'))
    # except:
    #     flash('Please check that your file extensions are allowed.')
    # #     raise Exception('Something went wrong')

    return render_template('upload.html', form=form)


#-----------------------UPLOAD_IMAGE-------------------------


# start aws session for img and model uploads
client = boto3.client('s3', 
                        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                        region_name=Config.AWS_REGION)

def upload_image():
 
    # get werkzeugfile from request dict
    file = request.files["image"]
    
    # standard flask security
    image_name = secure_filename(file.filename)
    
    # set image name to what the user is calling it
    object_name = image_name

    # test prints
    # print('*** test pint ->', file)
    # print('*** test pint ->', file.filename)
    # print('*** test pint ->', Config.UPLOAD_FOLDER + file.filename)

    # file MUST get saved for werkzeug to function! (otherwise is discarded immediately)
    file.save(os.path.join(Config.UPLOAD_FOLDER, image_name))


    # -------- max image size test ---------
    image_size = os.stat(Config.UPLOAD_FOLDER + image_name).st_size
    if image_size > 1024000:
        abort(400, '⚠ Image file is too large - it needs to be smaller than 1MB')
    # -------- max image size test ---------

    # upload to aws3, must include: name, bucket, and object name (min)
    client.upload_file(Config.UPLOAD_FOLDER + image_name, 
                        Config.AWS_BUCKET_NAME, 
                        object_name,
                        ExtraArgs={'ACL': 'public-read',
                                    'ContentType':'image/jpeg'})

    return image_name

    # ----- local project storage -----
    # print(Config.UPLOAD_FOLDER)
    # print(file)
    # file.save(os.path.join(Config.UPLOAD_FOLDER, file.filename))
    # return '../../static/uploads/' + file.filename  #directory file path (static) + file name
    

#-----------------------UPLOAD_MODEL-------------------------
def upload_model():

    # get werkzeugfile from request dict
    file = request.files["model"]

    # standard flask security
    model_name = secure_filename(file.filename)

    # set object name to what the user is calling it
    object_name = model_name
    
    # file MUST get saved for werkzeug to function!
    file.save(os.path.join(Config.UPLOAD_FOLDER, model_name))

    # -------- max model size test ---------
    model_size = os.stat(Config.UPLOAD_FOLDER + model_name).st_size
    if model_size > 5120000:
        abort(400, '⚠ Model file is too large - it needs to be smaller than 1MB')
    # -------- max model size test ---------

    # upload to aws3, must include: name, bucket, and object name (min)
    client.upload_file(Config.UPLOAD_FOLDER + model_name, 
                        Config.AWS_BUCKET_NAME, 
                        # Config.BUCKETEER_BUCKET_NAME, 
                        object_name,
                        ExtraArgs={'ACL': 'public-read-write'})
    return model_name

    # ----- local project storage -----
    # file.save(os.path.join(Config.UPLOAD_FOLDER, file.filename))
    # return '../../static/uploads/' + file.filename 

#-----------------------UPDATE_POST-------------------------
# def update_image():
#     if request.files:  
#         file = request.files["image"]
#     file.save(os.path.join(Config.UPLOAD_FOLDER, file.filename))
#     return '../../static/uploads/' + file.filename

# def update_model():
#     if request.files:  
#         file = request.files["model"]
#     file.save(os.path.join(Config.UPLOAD_FOLDER, file.filename))
#     return '../../static/uploads/' + file.filename 

@auth.route('/update/<id>', methods = ['GET', 'POST', 'PUT'])
@login_required
def update_post(id):
    form = ObjectUploadForm()
    post_update = Post.query.get(id)

    if request.method == 'POST':
        post_update.title = request.form['title']
        post_update.description = request.form['description']
        post_update.dimensions = request.form['dimensions']
        post_update.weight = request.form['weight']
        # post_update.img_url = request.form[update_image()]
        # post_update.title = request.form[update_model()]
        post_update.id = id
        post_update.user_id = post_update.user_id
        try:
            db.session.commit()
            post_schema.dump(post_update)
            flash("Update Successful!")
            render_template('update.html', form=form, post_update = post_update)
            return redirect(url_for('site.inventory'))
        except:
            # flash("Update Error, try again!")
            return render_template('update.html', form=form, post_update = post_update)
    else:
        return render_template('update.html', form=form, post_update = post_update)

#--------------------------DOWNLOAD----------------------
@auth.route('/', methods = ['GET', 'POST'])  #url path doesn't seem to affect anything, investigate this

# @login_required
def download():

    #----------local download code----------
    # try:
    return send_from_directory(Post.model_url)
        # os.path.join(Config.UPLOAD_FOLDER, file.filename), filename=model_url, as_attachment=True )

    # except FileNotFoundError:
    #     abort(404)

#------------------------DELETE------------------------

@auth.route('/delete/<id>', methods = ['GET'])
@login_required
def delete_post(id):
    #id passed in from JinJa
    post = Post.query.get(id)  #gets the db row via id
    # post = Post.query.get_or_404(id)  #tutorial code, this works too
    
    # remove objects from aws FIRST!
    print('*** - ', post.img_url)
    print('*** - ', post.model_url)
    client.delete_object(Bucket=Config.AWS_BUCKET_NAME, Key=post.img_url)
    client.delete_object(Bucket=Config.AWS_BUCKET_NAME, Key=post.model_url)

    db.session.delete(post)
    db.session.commit()
    post_schema.dump(post)

    return redirect(url_for('site.inventory'))

#-------------------------BUY-----------------------

@auth.route('/inventory', methods = ['GET','POST'])  #de-bug this
def seller_email():
    flash(f'Purchase feature comming soon!!')
    # return redirect(url_for('site.inventory'))

#----------------------LOGOUT--------------------------

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('site.home'))

