import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# Give access to the project in ANY OS we find ourselves in
# Allow outside files/folders to be added to the project from the base directory

load_dotenv(os.path.join(basedir, '.env'))

class Config():
    """
        Set Config variables for the flask app.
        Using Environment variables where available otherwise
        create the config variable if not done already.
    """
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_ENV = os.environ.get('FLASK_ENV')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'You will never guess'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DEPLOY_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Turn off update messages from the sqlalchemy

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS')

    #CLIENT_IMAGES = 
    #CLIENT_3DMODELS = 
    #MAX_IMAGE_FILESIZE = 5 * 1024 * 1024
    #MAX_3DMODEL_FILESIZE = 10 * 1024 * 1024
