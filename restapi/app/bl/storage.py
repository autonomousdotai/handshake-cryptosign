
import os
import re
import app.constants as CONST

from flask import g
from app.helpers.utils import current_milli


def delete_file(path_file):
    try:
        os.remove(path_file)    
    except Exception as ex:
        print(str(ex))


def handle_upload_file(file):
    file_name = formalize_filename(file.filename)
    saved_path = os.path.join(g.UPLOAD_DIR, file_name)
    file.save(saved_path)
    return file_name, saved_path


def formalize_filename(filename):
    # '/[^a-z0-9\_\-\.]/'
    file_name = re.sub(r'[^A-Za-z0-9\_\-\.]+', '_', filename)
    file_name = file_name.replace('.', '-' + str(current_milli()) + '.')
    return file_name


def validate_extension(filename):
    return '.' in filename and filename.split('.')[1] in CONST.UPLOAD_ALLOWED_EXTENSIONS
