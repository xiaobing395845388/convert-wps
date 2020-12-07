# * Title: convert<br>
# * Description: convert<br>
# * Copyright: Copyright (c) 2019<br>
# * Company: 华宇（大连）信息服务有限公司<br>
# * 
# * @author wangbing
# * @date 2020-10-10
# * @version 1.0

import os
import sys
import uuid
import subprocess

from pywpsrpc.rpcwpsapi import (createWpsRpcInstance, wpsapi)
from pywpsrpc.common import (S_OK, QtApp)

from starlette.requests import Request
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import JSONResponse
from starlette.templating import Jinja2Templates
from starlette.responses import FileResponse
from apscheduler.schedulers.background import BackgroundScheduler

formats = {
    "doc": wpsapi.wdFormatDocument,
    "docx": wpsapi.wdFormatXMLDocument,
    "rtf": wpsapi.wdFormatRTF,
    "html": wpsapi.wdFormatHTML,
    "pdf": wpsapi.wdFormatPDF,
    "xml": wpsapi.wdFormatXML,
}

app = FastAPI()
templates = Jinja2Templates(directory="templates")
base_path = "/headless/temp_file" 

def worker():
    path = base_path + "/out"
    if os.path.exists(path):
        for f in os.listdir(path):
            try:
                os.remove(path + "/" + f)
            except IOError:
                print("Error: 没有找到文件或读取文件失败" + path + "/" + f)
    if os.path.exists(base_path):
        for f in os.listdir(base_path):
            file_path = base_path + "/" + f
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except IOError:
                    print("Error: 没有找到文件或读取文件失败" + file_path)

scheduler = BackgroundScheduler()
scheduler.add_job(worker,'cron',day_of_week ='0-6',hour = 0,minute = 0)
scheduler.add_job(worker,'cron',day_of_week ='0-6',hour = 13,minute = 13)
scheduler.start() 

class ConvertException(Exception):

    def __init__(self, text, hr):
        self.text = text
        self.hr = hr

    def __str__(self):
        return """Convert failed:
Details: {}
ErrCode: {}
""".format(self.text, hex(self.hr & 0xFFFFFFFF))

def init(re_init):
    if re_init:
        subprocess.call("ps -ef|grep wps |awk '{print $2}'|xargs kill -9", shell = True)
    hr, rpc = createWpsRpcInstance()
    if hr != S_OK:
        raise ConvertException("Can't create the rpc instance", hr)
    hr, wps = rpc.getWpsApplication()
    if hr != S_OK:
        raise ConvertException("Can't get the application", hr)
    wps.Visible = False
    return wps.Documents
    
docs = init(False)

def doConvert(contents, fileType):
    file_name = str(uuid.uuid1())
    path = os.path.join(base_path ,file_name)
    os.makedirs(base_path, exist_ok=True)
    with open(path,'wb') as f:
        f.write(contents)
    global docs
    try:
        hr, doc = docs.Open(path, ReadOnly=True)
        if hr != S_OK:
            docs = init(True)
            hr, doc = docs.Open(path, ReadOnly=True)
            if hr != S_OK:
                raise ConvertException("Can't open file in path", hr)
        out_dir = base_path + "/out"
        os.makedirs(out_dir, exist_ok=True)
        new_path = out_dir + "/" + file_name  + "." + fileType
        doc.SaveAs2(new_path, FileFormat=formats[fileType])
        doc.Close(wpsapi.wdDoNotSaveChanges)   
        return  FileResponse(new_path, filename = file_name  + "." + fileType)
    except ConvertException as e:
        print(e)
        return JSONResponse(status_code=500, content = str(e))


@app.get("/")
async def test(request: Request):
    return templates.TemplateResponse('post.html', {'request': request})

@app.post('/api/v1/convert/wps/pdf')
async def convert(
                        request: Request,
                        file: UploadFile   = File(...)
                      ):
    contents = await file.read()
    return doConvert(contents, "pdf")

@app.get("/convert")
async def test(request: Request):
    return templates.TemplateResponse('convert.html', {'request': request})

@app.post('/api/v1/convert')
async def convert(
                        request: Request,
                        fileType: str = Form(...),
                        file: UploadFile   = File(...)
                      ):
    contents = await file.read()
    return doConvert(contents, fileType)