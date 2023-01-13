import os, webbrowser

# import boto3
import aspose.threed as a3d

from flask import Blueprint, flash, render_template, request, \
      redirect, url_for, send_from_directory, send_file, abort, session

from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename

# project file imports
from website.forms import UserLoginForm, ObjectUploadForm, UserSignupForm
from website.models import User, Post, db, check_password_hash, post_schema, posts_schema
from config import Config
from helpers import s3_client, ProgressPercentage, delete_files_from_s3, \
                    upload_file_to_s3, extension_checker, upload_model

auth = Blueprint('auth', __name__, template_folder ='auth_templates')

#----------------------SIGN_UP--------------------------
@auth.route('/signup', methods = ['GET','POST'])
def signup():
    form = UserSignupForm()

    try:
        if request.method == 'POST' and form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            print(email, password)

            # check to see if email/user account already exists, reject if so
            if User.query.filter_by(email=form.email.data).first():
                print(email, 'account already in db')
                flash(f'{email} already has an account with us. Please select a different email/user name.','auth-failed')
                return redirect(url_for('auth.signup'))

            # otherwise add the user acocunt info to db
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
                flash('You were successfully logged in, welcome back!', 'auth-success')
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

        #check IMAGE existance / extension before processing db update:
        # if not request.files["image"]:
        #     flash('⚠ Please attach a preview image file')
        #     return render_template('upload.html', form=form)
        # else:
        #     uploadimage = request.files["image"].filename
        #     image_ext = os.path.splitext(uploadimage)[1].lower()
        #     if image_ext not in Config.ALLOWED_IMAGES:
        #         flash('⚠ Image extension not allowed')
        #         return render_template('upload.html', form=form)

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
        
        # load db variables here
        title = form.title.data
        description = form.description.data
        price = form.price.data
        dimensions = form.dimensions.data
        weight = form.weight.data
        # img_url = upload_image()

        model_url = upload_model(request.files["model"])

        glb = model_url
        stl = extension_checker(request.files["model"], 'stl')
        obj = extension_checker(request.files["model"], 'obj')
        studio_max = extension_checker(request.files["model"], '3ds')
        dae = extension_checker(request.files["model"], 'dae')
        skp = extension_checker(request.files["model"], 'skp')

        user_id = current_user.id

        print(title, description, price, dimensions, weight, 
                model_url, glb, stl, obj, studio_max, dae, skp, 
                user_id)
        
        post = Post(title, description, price, dimensions, weight, 
                    model_url, glb, stl, obj, studio_max, dae, skp, 
                    user_id)

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('site.item', Config=Config, id=post.id))

    return render_template('upload.html', form=form)


#-----------------------UPLOAD_IMAGE-------------------------
# def upload_image():
#     # after confirm 'user_file' exist, get the file from input
#     file = request.files["image"]
#     # standard flask security
#     image_name = secure_filename(file.filename)

#     # ----------------UPLOAD_IMAGE ^^-------------------------
#     # set image name to what the user is calling it
#     object_name = image_name

#     # file MUST get saved for werkzeug to function! (otherwise is discarded immediately)
#     file.save(os.path.join(Config.UPLOAD_FOLDER, image_name))
#     print('file save - ', os.path.join(Config.UPLOAD_FOLDER, image_name))
#     print('conc file path -', Config.UPLOAD_FOLDER + image_name)
#     # -------- max image size test ---------
#     image_size = os.stat(Config.UPLOAD_FOLDER + image_name).st_size
#     if image_size > 1024000:
#         abort(400, '⚠ Image file is too large - it needs to be smaller than 1MB')
#     # -------- max image size test ---------
#     # upload to aws3, must include: name, bucket, and object name (min)
#     s3_client.upload_file(Config.UPLOAD_FOLDER + image_name, 
#                         Config.AWS_BUCKET_NAME, 
#                         object_name,
#                         ExtraArgs={'ACL': 'public-read', 'ContentType':'image/jpeg'},
#                         Callback=ProgressPercentage(Config.UPLOAD_FOLDER + image_name))
#     return image_name

        # ----- local project storage -----
        # print(Config.UPLOAD_FOLDER)
        # print(file)
        # file.save(os.path.join(Config.UPLOAD_FOLDER, file.filename))
        # return '../../static/uploads/' + file.filename  #directory file path (static) + file name

#-----------------------UPDATE_POST-------------------------

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
        # post_update.title = request.form[update_model()]
        post_update.id = id
        post_update.user_id = post_update.user_id

        try:
            db.session.commit()
            post_schema.dump(post_update)
            flash("Update Successful!")
            render_template('update.html', form=form, post_update=post_update)
            # return redirect(url_for('site.inventory'))
            return redirect(url_for('site.item', id=post_update.id))

        except:
            return render_template('update.html', form=form, post_update=post_update)

    else:
        return render_template('update.html', form=form, post_update=post_update)

#--------------------------DOWNLOAD----------------------
@auth.route('/', methods = ['GET', 'POST'])  #url path doesn't seem to affect anything, investigate this
# @login_required
def download(id):
    # try:
    post = Post.query.get(id)
    return send_from_directory(post.model_url)
        # os.path.join(Config.UPLOAD_FOLDER, file.filename), filename=model_url, as_attachment=True )
    # except FileNotFoundError:
    #     abort(404)

#-----------CONVERT 3D FILES---------------
@auth.route('/generate_file_type/<id>:<name>', methods = ['GET', 'POST'])
def generate_file_type(id,name):
    post = Post.query.get(id)
    
    # model_extension =  post.model_url.split('.')[-1]

    #download gbl file from s3 to flask server prior to conversion
    s3_client.download_file(Config.AWS_BUCKET_NAME, 
                            post.glb, 
                            Config.UPLOAD_FOLDER + post.glb)
    
    available_gbl_file = Config.UPLOAD_FOLDER + post.glb

    #get flask saved file
    scene = a3d.Scene.from_file(available_gbl_file)

    converted_model_file = post.glb.replace('glb', name)
    print(name, converted_model_file)
    scene.save(Config.UPLOAD_FOLDER + converted_model_file)
    upload_file_to_s3(converted_model_file)
    # flask_server_temp_upload = os.path.join(Config.UPLOAD_FOLDER, converted_model_file)
    
    # post.studio_max = converted_model_file
    if name == '3ds':
        post.studio_max = converted_model_file
        db.session.commit()
        webbrowser.open(Config.AWS_PUBLIC_URL + '/' + post.studio_max)
        # send_from_directory(Config.UPLOAD_FOLDER, post.studio_max)
    elif name == 'obj':
        post.obj = converted_model_file
        db.session.commit()
        print(Config.AWS_PUBLIC_URL + '/' + post.obj)
        webbrowser.open(Config.AWS_PUBLIC_URL + '/' + post.obj)
        # send_from_directory(Config.UPLOAD_FOLDER, post.obj)
    elif name == 'stl':
        post.stl = converted_model_file
        db.session.commit()
        webbrowser.open(Config.AWS_PUBLIC_URL + '/' + post.stl)
        # send_from_directory(path=post.stl)
    elif name == 'dae':
        post.dae = converted_model_file
        db.session.commit()
        webbrowser.open(Config.AWS_PUBLIC_URL + '/' + post.dae)
        # send_from_directory(path=post.dae)
    
    return render_template('item.html', Config=Config, post=post)

#------------------------DELETE------------------------

@auth.route('/delete/<id>', methods = ['GET'])
@login_required
def delete_post(id):

    #get the db row via id
    post = Post.query.get(id)  
    print(post, type(post))

    # remove objects from aws FIRST!
    delete_files_from_s3(post)

    db.session.delete(post)
    db.session.commit()
    post_schema.dump(post)

    return redirect(url_for('site.profile'))

#----------------------LOGOUT--------------------------

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('site.home'))

