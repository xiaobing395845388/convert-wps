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
import logging
import time

from pywpsrpc.rpcwpsapi import (createWpsRpcInstance, wpsapi)
from pywpsrpc.common import (S_OK, QtApp)

from starlette.requests import Request
from fastapi import FastAPI, Form, File, UploadFile, Path
from fastapi.responses import JSONResponse
from starlette.templating import Jinja2Templates
from starlette.responses import FileResponse

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

def log():
    #创建logger，如果参数为空则返回root logger
    logger = logging.getLogger("nick")
    #设置logger日志等级
    logger.setLevel(logging.ERROR)
    #这里进行判断，如果logger.handlers列表为空，则添加，否则，直接去写日志
    log_path = "/headless/log"
    log_name = "error.log"
    path = os.path.join(log_path ,log_name)
    if not os.path.exists(path):
        os.makedirs(log_path, exist_ok=True)
        os.mknod(path)
    if not logger.handlers:
        #创建handler
        fh = logging.FileHandler(path,encoding="utf-8")
        ch = logging.StreamHandler()
         #设置输出日志格式
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s",
            datefmt="%Y/%m/%d %X"
            )
        #为handler指定输出格式
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        #为logger添加的日志处理器
        logger.addHandler(fh)
        logger.addHandler(ch)
    return logger

logger = log()

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
            startConvertTime = time.time()
            doc.SaveAs2(new_path, FileFormat=formats[fileType])
            endConvertTime = time.time()
            convertTime = endConvertTime - startConvertTime
            logger.info("文件转换耗时%s：%s" % (file_name, convertTime))
            doc.Close(wpsapi.wdDoNotSaveChanges)
            startReturnTime = time.time()
            return  FileResponse(new_path, filename = file_name  + "." + fileType)
        except ConvertException as e:
            print(e)
            logger.error("文件转换异常:" + str(e))
            return JSONResponse(status_code=500, content = str(e))
        except Exception as e:
            logger.error("文件转换异常:" + str(e))
            return JSONResponse(status_code=500, content = str(e))
        else:
            endReturnTime = time.time()
            returnTime = endReturnTime - startReturnTime
            logger.info("文件返回客户端耗时：%s" % returnTime)
    else:
        return JSONResponse(status_code=500, content = str("格式类型转换暂不支持：" + fileType))
