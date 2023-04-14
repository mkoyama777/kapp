import json
import pathlib
import os
import random
import uuid
import shutil
# import yoloface.yoloface as yolo
import iccardmodel.iccard as iccard
import threading
import glob
from PIL import Image
from datetime import *
from flask import *
from pathlib import Path
from werkzeug.utils import secure_filename
from concurrent.futures import ProcessPoolExecutor
from linebot import *
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import time
import numpy as np
UPLOAD_FOLDER = 'upload'
OUTPUT_FOLDER = 'output'
# UPLOAD_FOLDER = os.path.abspath(UPLOAD_FOLDER)
# OUTPUT_FOLDER = os.path.abspath(OUTPUT_FOLDER)

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
    uuiddata = get_uuid(request)
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

def check(request,session):
    arr = {}
    uuiddata = get_uuid(request)
    # print(uuiddata)
    inputdir = get_abs_uploaddir(request)
    outputdir = get_abs_outputdir(request)
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


def upload(request,session):
    
    trackingtype = request.form['trackingtype']
    file = request.files['upfile']

    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        arr = session["filenames"]
        procflg = filename in arr
        arr[filename] = False
        #ファイル保存
        inputdir = get_abs_uploaddir(request)
        outputdir = get_abs_outputdir(request)
        outputfilename = changesuffix(filename)
        file.save(os.path.join(inputdir, filename))
        inputfilepath = os.path.join(inputdir, filename)
        outputfilepath = os.path.join(outputdir, outputfilename)
        if(not os.path.exists(outputfilepath)):
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
    arr = session["filenames"]
    arr.pop(fname)
    session["filenames"] = arr
    upload_fname = get_abs_uploaddir(request) + os.sep + fname
    output_fname = get_abs_outputdir(request) + os.sep + fname
    os.remove(upload_fname)
    os.remove(output_fname)
    
    return json.dumps({'code':200,'filenames':session["filenames"]})          

def download(request,session):
  print("---download start")
  fname = request.args.get('outputfname')
  dirname = get_outputdir(request)
  if(fname == None):
    fname = request.args.get('inputfname')
    dirname = get_uploaddir(request)

  print(dirname)
  print(dirname+ os.sep +fname)
  print("---------download")
  abs_dirname = get_abs_outputdir(request)
#   return send_file(
#       dirname,
#       fname,
#       as_attachment=True,
#   )
        # directory=dirname,
        # filename=fname,
        # path=dirname+ os.sep +fname,
        # as_attachment=True,
        # attachment_filename=fname)      
  return send_from_directory(
        dirname,
        fname,
        as_attachment=True)
        # directory=dirname,
        # filename=secure_filename(fname),
        # path=abs_dirname + os.sep +fname,
        # as_attachment=True)
        # attachment_filename=fname)    
print("-----------LINE API 初期化")
handler = WebhookHandler("35346a0da38fce1d5e481ba009457c12")  
# LINE Bot APIクライアントの初期化
line_bot_api = LineBotApi("TjTs9XIJkLk0SogrGYT/uskhphTWH6UDL6lFtaHYWEG6mUHcZ8trV2f+brXv+2RlAZdgQWIgvYICMiMkVyJDD2X2cCorXwSQaPEl4rNXoqlg6Qnk/+Xu1TW06YSNDQTe8GTRmUM356WICWryg0mbUAdB04t89/1O/w1cDnyilFU=")
print("-----------LINE API 初期化 END")
    
def webhook(request,session):
    print("---------webhook")
    
    #LINEのWEBHOOkからのリクエストを受け取る
    signature = request.headers['X-Line-Signature']
    body_base = request.get_data(as_text=True)
    print("---------request")
    print(body_base)
    #JSONを配列に変換する
    body = json.loads(body_base)
    msgtype = body['events'][0]['message']['type']
    #ユーザIDを取得する
    line_id = body['events'][0]['source']['userId']
    
    #リクエストがLINE Platformから送られてきたものか検証する
    try:
        handler.handle(body_base, signature)
    except InvalidSignatureError as e:
        print(e)
        raise e
    print("189")
    #LINEより受信したリクエストがテキストか画像かを判定する
    if msgtype == "image":
        uuiddata = reset(request)
        print("image")
        inputdir = get_abs_uploaddir(request,uuiddata)
        print("195")
        #ファイル名を取得する
        return "OK"
        #LINEから画像を取得する
        message_content = line_bot_api.get_message_content(body['events'][0]['message']['id'])
        filename = "line.jpg"
        inputfilename = inputdir + os.sep +  filename
        print("inputを保存")
        #画像をinputディレクトリに保存する
        with open(inputfilename, 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
        #ファイルをクローズする
        fd.close()
        
        #1秒待つ
        # time.sleep(2)
        #性別を推論する。
        print("推論開始")
        # sex,age = yolo.analyze("image",inputfilename)
        
        outputdir = None
        outputfilename = None
        print("Lineid:"+line_id)
        # th = threading.Thread(target=yolo.analyze,args=[get_filetype(filename),inputfilename,outputdir,outputfilename,line_id])
        # th.start()
        print(inputfilename)
        # try:
        #     print("ファイルサイズ:"+os.path.getsize(inputfilename))
        # except Exception as e:
        #     print(e)
        img = Image.open(inputfilename)
        img_array = np.array(img)
        print("predict")
        label = iccard.predict(img_array)
        # print("性別:"+sex)
        # print("年齢:"+age)
        #年齢を性別する。
        #性別/年齢をレスポンスで返す
        #リクエストを受け取ったことをLINEに返す
        print("reply")
        line_bot_api.reply_message(body['events'][0]['replyToken'],TextSendMessage(text=label))

    else:
        print("対象外type")    


    #画像の場合はuuidを生成する。
    #inputディレクトリにファイルを保存する
    
    #性別を推論する。
    #年齢を性別する。

    #性別/年齢をレスポンスで返す   
 

    #リクエストを受け取ったことをLINEに返す

    return 'OK'

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
    
def get_uuid(request):
    uuiddata = request.cookies.get('_kapp_uuid', None)
    if uuiddata is None:
        print("make new uuid")
        uuiddata = str(uuid.uuid1())

    return uuiddata

def get_abs_uploaddir(request,uuiddata = None):    
    return os.path.abspath(get_uploaddir(request,uuiddata))

def get_abs_outputdir(request):    
    return os.path.abspath(get_outputdir(request))

def get_uploaddir(request,uuiddata = None):    
    key = uuiddata
    if key is None:
        key = get_uuid(request)
    
    return UPLOAD_FOLDER + os.sep + key

def get_outputdir(request):    
    key = get_uuid(request)
    return OUTPUT_FOLDER + os.sep + key
    