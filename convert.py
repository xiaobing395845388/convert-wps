import os
import sys
import argparse

from pywpsrpc.rpcwpsapi import (createWpsRpcInstance, wpsapi)
from pywpsrpc.common import (S_OK, QtApp)
from fastapi import FastAPI

from starlette.requests import Request
from fastapi import FastAPI, Form, File, UploadFile
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

class ConvertException(Exception):

    def __init__(self, text, hr):
        self.text = text
        self.hr = hr

    def __str__(self):
        return """Convert failed:
Details: {}
ErrCode: {}
""".format(self.text, hex(self.hr & 0xFFFFFFFF))

def convert_to(path, format, abort_on_fails=False):
    try:
        new_path = convert_to(path, "pdf", False)
        hr, rpc = createWpsRpcInstance()
        if hr != S_OK:
        raise ConvertException("Can't create the rpc instance", hr)

    hr, app = rpc.getWpsApplication()
    if hr != S_OK:
        raise ConvertException("Can't get the application", hr)

    # we don't need the gui
    app.Visible = False

    docs = app.Documents

    def _handle_result(hr):
        if abort_on_fails and hr != S_OK:
            raise ConvertException("convert_file failed", hr)

    hr, doc = docs.Open(path, ReadOnly=True)
    if hr != S_OK:
        return hr

    out_dir = os.path.dirname(os.path.realpath(path)) + "/out"
    os.makedirs(out_dir, exist_ok=True)

    # you have to handle if the new_file already exists
    new_path = out_dir + "/" + os.path.splitext(os.path.basename(path))[0] + "." + format
    doc.SaveAs2(new_path, FileFormat=formats[format])

    # always close the doc
    doc.Close(wpsapi.wdDoNotSaveChanges)
    _handle_result(hr)

    app.Quit()
    return new_path

@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse('post.html', {'request': request})

@app.post('/convert')
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
        new_path = convert_to(path, "pdf", False)
        return  FileResponse(new_path, filename=file.filename.split(".")[0]+".pdf")
    except ConvertException as e:
        print(e)
