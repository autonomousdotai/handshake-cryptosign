
import os
import re
import app.constants as CONST

from flask import g
from app.helpers.utils import current_milli


def check_folder_exists_or_create(folder_dir):
    # "Path" begin at "/app/"
    root_path = os.path.abspath(os.path.dirname(__file__)) + '/../'
    newpath = root_path + folder_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath

def delete_file(path_file):
    root_path = os.path.abspath(os.path.dirname(__file__)) + '/../'
    os.remove(os.path.join(root_path, path_file))
    return True

def handle_upload_file(file):
    # '/[^a-z0-9\_\-\.]/'
    file_name = re.sub(r'[^A-Za-z0-9\_\-\.]+', '_', file.filename)
    file_name = file_name.replace('.', '-' + str(current_milli()) + '.')
    tmp_folder = 'files/tmp/'
    path = check_folder_exists_or_create(tmp_folder)
    saved_path = os.path.join(path, file_name)
    file.save(saved_path)
    return file_name, saved_path
