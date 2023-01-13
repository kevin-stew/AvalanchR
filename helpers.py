import boto3, botocore, os, sys, threading
import aspose.threed as a3d
from werkzeug.utils import secure_filename
from config import Config
from flask import flash, abort
from ast import literal_eval

# start aws session for img and model uploads
s3_client = boto3.client('s3', 
                        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                        region_name=Config.AWS_REGION)

class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()
    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write("\r%s  %s / %s  (%.2f%%)" % (self._filename, self._seen_so_far, self._size, percentage))
            sys.stdout.flush()
            print(' status %')

# def upload_file_to_s3(file, acl="public-read"):

#     filename = secure_filename(file.filename)
#     try:
#         # save file to server via werkzeug
#         filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
#         file.save(filepath)
        
#         print(file)
#         print(filepath)

#         # send file to s3 from server
#         s3_client.upload_fileobj(Config.UPLOAD_FOLDER + file.filename, 
#                                 Config.AWS_BUCKET_NAME, 
#                                 filename, 
#                                 ExtraArgs={"ACL": acl, "ContentType": file.content_type},
#                                 # Callback=ProgressPercentage('./uploads/' + filename)
#                                 )

#     except Exception as e:

#         # This is a catch all exception, edit this part to fit your needs.
#         print("Something Happened: ", e)
#         abort(404)
#         # return e
    
#     # after upload file to s3 bucket, return filename of the uploaded file
#     return filename
def upload_file_to_s3(model_file):
     s3_client.upload_file(Config.UPLOAD_FOLDER + model_file, 
                        Config.AWS_BUCKET_NAME, 
                        model_file,
                        ExtraArgs={'ACL': 'public-read-write'},
                        Callback=ProgressPercentage(Config.UPLOAD_FOLDER + model_file)
                        )

def delete_files_from_s3(post):
    if post:
        # s3_client.delete_object(Bucket=Config.AWS_BUCKET_NAME, Key=post.img_url)
        # s3_client.delete_object(Bucket=Config.AWS_BUCKET_NAME, Key=post.glb)

        files_to_delete = [post.glb, 
                           post.studio_max, 
                           post.stl, 
                           post.obj, 
                           post.dae, 
                           post.skp]
                           
        for file in files_to_delete:
            if file:
                s3_client.delete_object(Bucket=Config.AWS_BUCKET_NAME, Key=file)

        print(literal_eval(Config.ALLOWED_MODELS), type(literal_eval(Config.ALLOWED_MODELS)))

        return post

    else:
        flash('Please indicate a post to delete!')

#------------------pre-upload functions-------------
def extension_checker(file, extension_type_check):
    model_name = file.filename
    model_extension =  model_name.split('.')[-1]
    if model_extension == extension_type_check:
        return model_name
    else: 
        return None

def check_model_size(model_name):
    model_size = os.stat(Config.UPLOAD_FOLDER + model_name).st_size
    if model_size > 5120000:
        abort(400, '⚠ Model file is too large - it needs to be smaller than 1MB')

#-----------------------UPLOAD_MODEL-------------------------
def upload_model(file):
    # get werkzeugfile from request dict
    # file = request.files["model"]
    # standard flask security
    model_name = secure_filename(file.filename)
    # -------------------------
    # file MUST get saved for werkzeug to function!
    file.save(os.path.join(Config.UPLOAD_FOLDER, model_name))

    # -------- max model size test ---------
    check_model_size(model_name)

    # -------- create .glb if not ---------
    model_extension =  model_name.split('.')[-1]

    if model_extension == 'glb':
        upload_file_to_s3(model_name)
        return model_name

    elif model_extension != 'glb':
        #save OG file and .glb to flask server uploads folder
        scene = a3d.Scene.from_file(Config.UPLOAD_FOLDER + model_name)
        glb_model = model_name.replace(model_extension, 'glb')
        scene.save(Config.UPLOAD_FOLDER + glb_model)
        
    #send OG model and .glb file to s3
    upload_file_to_s3(model_name)
    upload_file_to_s3(glb_model)

    return glb_model



