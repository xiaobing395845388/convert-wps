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
import logging, logging.config
import time

from pywpsrpc.rpcwpsapi import (createWpsRpcInstance, wpsapi)
from pywpsrpc.common import (S_OK, QtApp)

from starlette.requests import Request
from fastapi import FastAPI, Form, File, UploadFile, Path
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse, StreamingResponse

formats = {
    "doc": wpsapi.wdFormatDocument,
    "docx": wpsapi.wdFormatXMLDocument,
    "rtf": wpsapi.wdFormatRTF,
    "html": wpsapi.wdFormatHTML,
    "pdf": wpsapi.wdFormatPDF,
    "xml": wpsapi.wdFormatXML,
}

media_types = {
    "html": "text/html",
    "pdf":"application/pdf"
}

log_levels = {
    'debug': logging.DEBUG,
    'error': logging.ERROR,
    'info': logging.INFO
}

app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
base_path = "/headless/temp_file"

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

#log
log_path = "/headless/log"
log_name = "error.log"
path = os.path.join(log_path ,log_name)
if not os.path.exists(log_path):
    os.makedirs(log_path, exist_ok=True)
    os.mknod(path)

logging.config.fileConfig("/headless/log.conf")

def setLogLevel():
    global level
    if 'LOG_LEVEL' in os.environ and os.environ['LOG_LEVEL'] in log_levels:
        log_level = os.environ['LOG_LEVEL'].lower()
        level = log_levels[log_level]
    else:
        level = logging.ERROR
    logger = logging.getLogger()
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
    return logger

logger = setLogLevel()

@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@app.post('/api/v1/convert/wps/{fileType}')
async def convert(request: Request, file: UploadFile = File(...), fileType: str = Path(..., description="目标文件类型,支持：doc、docx、rtf、html、pdf、xml")):
    if fileType in formats:
        file_name = str(uuid.uuid1())
        path = os.path.join(base_path ,file_name)
        os.makedirs(base_path, exist_ok=True)
        contents = await file.read()
        with open(path,'wb') as f:
            f.write(contents)
        global docs
        global new_path
        global start_returnTime
        try:
            hr, doc = docs.Open(path, PasswordDocument="xxx", ReadOnly=True)
            if hr != S_OK:
                docs = init(True)
                hr, doc = docs.Open(path, PasswordDocument="xxx", ReadOnly=True)
                if hr != S_OK:
                    raise ConvertException("Can't open file in path", hr)
            out_dir = base_path + "/out"
            os.makedirs(out_dir, exist_ok=True)
            new_path = out_dir + "/" + file_name  + "." + fileType
            start_convertTime = time.time()
            doc.SaveAs2(new_path, FileFormat=formats[fileType])
            convertTime = time.time() - start_convertTime
            logger.info("文件转换耗时%s：%s" % (file_name, convertTime))
            doc.Close(wpsapi.wdDoNotSaveChanges)
            start_returnTime = time.time()
            new_file = open(new_path,'rb')
            openTime = time.time() - start_returnTime
            logger.info("打开文件耗时%s" % openTime)
            return StreamingResponse(new_file, media_type= media_types[fileType])
        except Exception as e:
            logger.error("文件名称:" + file.filename + "转换失败，异常信息:" + str(e))
            return JSONResponse(status_code=500, content = str(e))
        finally:
            returnTime = time.time() - start_returnTime
            logger.info("文件返回客户端耗时：%s" % returnTime)
            clean(path, new_path)
    else:
        return JSONResponse(status_code=500, content = str("格式类型转换暂不支持：" + fileType))

# 转换文件之后 清理临时文件
def clean(path, new_path):
    logger.info("开始清除临时文件, 转换前文件路径：%s, 转换后文件路径：%s" % (path, new_path))
    if os.path.exists(path):
        try:
            os.remove(path)
        except IOError:
            logger.error("Error: 没有找到文件或读取文件失败 %s " % path)
    if os.path.exists(new_path):
        try:
            os.remove(new_path)
        except IOError:
            logger.error("Error: 没有找到文件或读取文件失败 %s " % new_path)
