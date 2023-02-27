import json
import pathlib
import os
import random
import uuid
import shutil
import yoloface.yoloface as yolo
import threading
import subprocess

from flask import *
from pathlib import Path
from datetime import timedelta 
from werkzeug.utils import secure_filename
from concurrent.futures import ProcessPoolExecutor


UPLOAD_FOLDER = 'upload'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = { '.png', '.jpg', '.jpeg', '.gif','.mp4'}

def index(request,session):
    session.permanent = True
    reset()
    return render_template('index.html')
def reset():
    if "uuid" in session:
        key = session['uuid'] 
    else:
        key = str(uuid.uuid1())
        session['uuid'] = key
        print()

    new_dir_path = UPLOAD_FOLDER+"/"+key
    new_output_path = OUTPUT_FOLDER+"/"+key
    if(os.path.exists(new_dir_path)): 
        shutil.rmtree(new_dir_path)
    if(os.path.exists(new_output_path)):    
        shutil.rmtree(new_output_path)
    os.makedirs(new_dir_path)        
    os.makedirs(new_output_path)
    session["filenames"] = {}            

def check(request,session,upload_dir,output_dir):
    arr = session["filenames"]
    key = session["uuid"]
    inputdir = upload_dir+"/"+key
    outputdir = output_dir+"/"+key

    for filename in arr:
        outputfilename = changesuffix(filename)
        if(os.path.exists(outputdir+"/"+outputfilename)):
            arr[filename] = outputfilename
    session["filenames"] = arr
    return json.dumps({'code':200,'filenames':session["filenames"]})


def upload(request,session,upload_dir,output_dir):
    trackingtype = request.form['trackingtype']
    file = request.files['upfile']
    key = session['uuid']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        arr = session["filenames"]
        procflg = filename in arr
        arr[filename] = False
        #ファイル保存
        inputdir = upload_dir+"/"+key
        outputdir = output_dir+"/"+key
        outputfilename = changesuffix(filename)
        file.save(os.path.join(inputdir, filename))
        inputfilepath = os.path.join(inputdir, filename)
        outputfilepath = os.path.join(outputdir, outputfilename)
        if(not os.path.exists(outputdir+"/"+outputfilename)):
            #Tracking
            if (not procflg):
                #処理中ではないので、解析を実行
                    # with ProcessPoolExecutor(max_workers=10) as executor:
                    #     {executor.submit(yolo.analyze(get_filetype(filename),inputfilepath,outputfilepath)  ) }
                print("call analyze")
                outputfilename = changesuffix(filename)
                # th = threading.Thread(target=yolo.analyze,args=[get_filetype(filename),inputfilepath,outputdir,outputfilename])
                subprocess.Popen("python ../yoloface/yoloface.py",[get_filetype(filename),inputfilepath,outputdir,outputfilename])
                cmd = ["yolo.sh",get_filetype(filename),inputfilepath,outputdir,outputfilename]
                subprocess.Popen(cmd,bufsize=1, shell=True)
                th.start()
                

        return json.dumps({'code':200,'filenames':session["filenames"]})          
    return json.dumps({'code':200,'message':'no file'})      

async def analyze(filename,inputpath,outputpath):
    print("call analyze async")
    yolo.analyze(get_filetype(filename),inputpath,outputpath)        

def delfile(request,session ):
    fname = request.form['fname']
    print("delfile:"+fname)
    arr = session["filenames"]
    arr.pop(fname)
    session["filenames"] = arr
    for fname in session["filenames"]:
        print(fname)
    return json.dumps({'code':200,'filenames':session["filenames"]})          

def download(request,session,upload_dir,output_dir):
  print("---download start")
  fname = request.args.get('outputfname')
  dirname = output_dir
  if(fname == None):
    fname = request.args.get('inputfname')
    dirname = upload_dir
  key = session['uuid']
  dirname = dirname +"/"+key
  print(dirname)
  print(dirname+"/"+fname)
  return send_from_directory(
        directory=dirname,
        filename=fname,
        path=dirname+"/"+fname,
        as_attachment=True,
        attachment_filename=fname)      

def changesuffix(filename):
    suffix = pathlib.Path(filename).suffix
    if(suffix == ".mp4"):
        return filename.replace(suffix, '.avi')
    return filename

def allowed_file(filename):
    suffix = pathlib.Path(filename).suffix
    
    if suffix in ALLOWED_EXTENSIONS:
        return True
    return False

def get_filetype(filename):
    suffix = pathlib.Path(filename).suffix
     #'.png', '.jpg', '.jpeg', '.gif','.mp4'}
    if (suffix == '.png' or suffix == '.jpg' or suffix == '.jpeg' or suffix == '.gif' ):
        return "image"
    if (suffix == '.mp4'):
        return "movie"
    