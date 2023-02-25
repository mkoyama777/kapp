import json
import pathlib
import os
import random
import uuid
import shutil
import subprocess

from flask import *
from pathlib import Path
from datetime import timedelta 
from werkzeug.utils import secure_filename

import controller.webcontroller as webctl

UPLOAD_FOLDER = 'upload'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg','.mp4'}

app = Flask(__name__)
app.secret_key = 'user'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.permanent_session_lifetime = timedelta(minutes=300) 

if(os.path.exists(UPLOAD_FOLDER)):
    shutil.rmtree(UPLOAD_FOLDER)
    os.mkdir(UPLOAD_FOLDER)
if(os.path.exists(OUTPUT_FOLDER)):    
    shutil.rmtree(OUTPUT_FOLDER)
    os.mkdir(OUTPUT_FOLDER)

@app.route('/')
def index():
    return webctl.index(request,session)

@app.route('/upload',methods=["POST"])
def upload():
    return webctl.upload(request,session,UPLOAD_FOLDER,OUTPUT_FOLDER)

@app.route('/check',methods=["POST"])
def check():
    return webctl.check(request,session,UPLOAD_FOLDER,OUTPUT_FOLDER)

@app.route('/delfile',methods=["POST"])
def delfile():
    return webctl.delfile(request,session)

@app.route("/download",methods=["GET"])
def download():
    return webctl.download(request,session,UPLOAD_FOLDER,OUTPUT_FOLDER)

@app.route("/init",methods=["GET"])
def init():
    subprocess.run("./yoloface/model_weights/get_models.sh")

if __name__ == "__main__":
    app.run(debug=True)