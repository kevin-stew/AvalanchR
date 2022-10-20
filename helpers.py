import boto3, botocore, os, sys, threading
from werkzeug.utils import secure_filename
from config import Config
from flask import flash, abort

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


def delete_file_from_s3(post):
    if post:
        s3_client.delete_object(Bucket=Config.AWS_BUCKET_NAME, Key=post.img_url)
        s3_client.delete_object(Bucket=Config.AWS_BUCKET_NAME, Key=post.model_url)
        return post
    else:
        flash('Please indicate a post to delete!')