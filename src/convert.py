# * Title: convert<br>
# * Description: convert<br>
# * Copyright: Copyright (c) 2020<br>
# * Company: 华宇（大连）信息服务有限公司<br>
# * 
# * @author wangbing
# * @date 2020-10-10
# * @version 1.0

import os
import sys

from pywpsrpc.rpcwpsapi import (createWpsRpcInstance, wpsapi)
from pywpsrpc.common import (S_OK, QtApp)

from starlette.requests import Request
from fastapi import FastAPI, Form, File, UploadFile
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

def worker():
    path = "temp_file/out"
    if os.path.exists(path):
        for f in os.listdir(path):
            os.remove(path + "/" + f)
    path = "tem_file/"
    if os.path.exists(path):
        for f in os.listdir(path):
            os.remove(path + "/" + f)

scheduler = BackgroundScheduler()
scheduler.add_job(worker,'cron',day_of_week ='0-6',hour = 00,minute = 00)
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

hr, rpc = createWpsRpcInstance()
if hr != S_OK:
    raise ConvertException("Can't create the rpc instance", hr)
hr, wps = rpc.getWpsApplication()
if hr != S_OK:
    raise ConvertException("Can't get the application", hr)
wps.Visible = False
docs = wps.Documents

@app.get("/")
async def test(request: Request):
    return templates.TemplateResponse('post.html', {'request': request})

@app.post('/api/v1/convert/wps/pdf')
async def convert(
                        request: Request,
                        file: UploadFile   = File(...)
                      ):    
    path = os.path.join("temp_file",file.filename)
    os.makedirs("temp_file/", exist_ok=True)
    contents = await file.read()
    with open(path,'wb') as f:
        f.write(contents)
    try:
        hr, doc = docs.Open(path, ReadOnly=True)
        if hr != S_OK:
            return hr
        out_dir = os.path.dirname(os.path.realpath(path)) + "/out"
        os.makedirs(out_dir, exist_ok=True)
        new_path = out_dir + "/" + os.path.splitext(os.path.basename(path))[0] + ".pdf"
        doc.SaveAs2(new_path, FileFormat=formats["pdf"])
        doc.Close(wpsapi.wdDoNotSaveChanges)   
        return  FileResponse(new_path, filename=file.filename.split(".")[0]+".pdf")
    except ConvertException as e:
        print(e)