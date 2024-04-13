
import os

from flask import send_from_directory

from app import create_app

from dotenv import load_dotenv

load_dotenv()

project_folder = os.path.expanduser('~/groma')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))


settings_module = os.getenv('APP_SETTINGS_MODULE')
app = create_app(settings_module)


@app.route('/media/posts/<filename>')
def media_posts(filename):
    dir_path = os.path.join(
        app.config['MEDIA_DIR'],
        app.config['POSTS_IMAGES_DIR'])
    return send_from_directory(dir_path, filename)
