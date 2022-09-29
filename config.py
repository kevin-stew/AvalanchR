import os
from dotenv import load_dotenv

# Give access to the project in ANY OS we find ourselves in
# Allow outside files/folders to be added to the project from the base directory
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config():
    """
        Set Config variables for the flask app.
        Using Environment variables where available otherwise
        create the config variable if not done already.
    """
    FLASK_APP=os.environ.get('FLASK_APP')
    FLASK_ENV=os.environ.get('FLASK_ENV')
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'You will never guess'

    SQLALCHEMY_DATABASE_URI=os.environ.get('DEPLOY_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS=False # Turn off update messages from the sqlalchemy

    UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER')
    ALLOWED_EXTENSIONS=os.environ.get('ALLOWED_EXTENSIONS')

    #CLIENT_IMAGES = 
    #CLIENT_3DMODELS = 
    #MAX_IMAGE_FILESIZE = 5 * 1024 * 1024
    #MAX_3DMODEL_FILESIZE = 10 * 1024 * 1024

    #Static Cloud file storage for user uploads : Bucketeer (AWS S3) 
    BUCKETEER_AWS_REGION=os.environ.get('BUCKETEER_AWS_REGION')
    BUCKETEER_AWS_ACCESS_KEY_ID=os.environ.get('BUCKETEER_AWS_ACCESS_KEY_ID')
    BUCKETEER_AWS_SECRET_ACCESS_KEY=os.environ.get('BUCKETEER_AWS_SECRET_ACCESS_KEY')
    BUCKETEER_AWS_BUCKET_NAME=os.environ.get('BUCKETEER_BUCKET_NAME')
    BUCKETEER_AWS_PUBLIC_URL=os.environ.get('BUCKETEER_PUBLIC_URL')
    
    AWS_REGION=os.environ.get('AWS_REGION')
    AWS_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_BUCKET_NAME=os.environ.get('AWS_BUCKET_NAME')
    AWS_PUBLIC_URL=os.environ.get('AWS_PUBLIC_URL')
