import boto3, os
from werkzeug.utils import secure_filename
from config import Config
from flask import flash

# start aws session for img and model uploads
s3_client = boto3.client('s3', 
                        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                        region_name=Config.AWS_REGION)

def upload_file_to_s3(file, acl="public-read"):

    filename = secure_filename(file.filename)

    try:
        s3_client.upload_fileobj(file, 
                          Config.AWS_BUCKET_NAME, 
                          file.filename, 
                          ExtraArgs={"ACL": acl, "ContentType": file.content_type}
                          )
                        #   Callback=ProgressPercentage(file.filename)
                        #   add this param ^^ once get able to work in test env

    except Exception as e:

        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)

        return e
    
    # after upload file to s3 bucket, return filename of the uploaded file
    return file.filename

def delete_file_from_s3(post):
    if post:
        s3_client.delete_object(Bucket=Config.AWS_BUCKET_NAME, Key=post.img_url)
        s3_client.delete_object(Bucket=Config.AWS_BUCKET_NAME, Key=post.model_url)
        return post
    else:
        flash('Please indicate a post to delete!')