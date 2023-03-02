import json
import pathlib
import os
import random
import uuid
import shutil
import yoloface.yoloface as yolo
import threading
import glob
from datetime import *
from flask import *
from pathlib import Path
from werkzeug.utils import secure_filename
from concurrent.futures import ProcessPoolExecutor


UPLOAD_FOLDER = 'upload'
OUTPUT_FOLDER = 'output'
UPLOAD_FOLDER = os.path.abspath(UPLOAD_FOLDER)
OUTPUT_FOLDER = os.path.abspath(OUTPUT_FOLDER)

ALLOWED_EXTENSIONS = { '.png', '.jpg', '.jpeg', '.gif','.mp4'}

def index(request,session):
    session.permanent = True
    uuiddata = reset(request)
    print("---make index uuiddata")
    print(uuiddata)
    response = make_response(render_template('index.html'))
    max_age = 60 * 60 * 24 * 120 # 120 days
    expires = int(datetime.now().timestamp()) + max_age
    response.set_cookie('_kapp_uuid', value=uuiddata, expires=expires)
    return response

def reset(request):
    uuiddata = request.cookies.get('_kapp_uuid', None)
    if uuiddata is None:
        print("make new uuid")
        uuiddata = str(uuid.uuid1())
    else:   
        print("uuid session exist")

    new_dir_path = UPLOAD_FOLDER+"/"+uuiddata
    new_output_path = OUTPUT_FOLDER+"/"+uuiddata
    if(os.path.exists(new_dir_path)): 
        # shutil.rmtree(new_dir_path)
        print("input dir exits")
    else:
        os.makedirs(new_dir_path)        
    if(os.path.exists(new_output_path)):    
        # shutil.rmtree(new_output_path)
        print("output dir exits")
    else:
        os.makedirs(new_output_path)    
    # os.makedirs(new_dir_path)        
    # os.makedirs(new_output_path)
    return uuiddata            

def check(request,session,upload_dir,output_dir):
    arr = {}
    uuiddata = request.cookies.get('_kapp_uuid', None)
    # print(uuiddata)
    inputdir = upload_dir+os.sep+uuiddata
    outputdir = output_dir+os.sep+uuiddata
    inputfiles = glob.glob(inputdir+os.sep+"*")
    # print(inputfiles)
    if uuiddata is None:
        print("uuiddata is none")
    else:
        for inputfile in inputfiles:
            # print("file")
            if(os.path.isfile(inputfile)):
                inputfile = os.path.basename(inputfile)
                arr[inputfile] = False
                outputfilename = changesuffix(inputfile)
                if(os.path.exists(outputdir+"/"+outputfilename) ):
                    arr[inputfile] = outputfilename
        session["filenames"] = arr
    return json.dumps({'code':200,'filenames':session["filenames"]})


def upload(request,session,upload_dir,output_dir):
    trackingtype = request.form['trackingtype']
    file = request.files['upfile']
    # key = session['uuid']
    key = request.cookies.get('_kapp_uuid', None)
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
        if(not os.path.exists(outputdir+os.sep+outputfilename)):
            #Tracking
            if (not procflg):
                #処理中ではないので、解析を実行
                    # with ProcessPoolExecutor(max_workers=10) as executor:
                    #     {executor.submit(yolo.analyze(get_filetype(filename),inputfilepath,outputfilepath)  ) }
                print("call analyze")
                outputfilename = changesuffix(filename)
                th = threading.Thread(target=yolo.analyze,args=[get_filetype(filename),inputfilepath,outputdir,outputfilename])
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
  key = request.cookies.get('_kapp_uuid', None)
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
    