#copyright (c) 2020 
# *
# * This file is part of pywpsrpc.
# *
# * This file is distributed under the MIT License.
# * See the LICENSE file for details.
# *
#*

import os
import sys
import socketserver

from pywpsrpc.rpcwpsapi import (createWpsRpcInstance, wpsapi)
from pywpsrpc.common import (S_OK, QtApp)
from apscheduler.schedulers.background import BackgroundScheduler

formats = {
    "doc": wpsapi.wdFormatDocument,
    "docx": wpsapi.wdFormatXMLDocument,
    "rtf": wpsapi.wdFormatRTF,
    "html": wpsapi.wdFormatHTML,
    "pdf": wpsapi.wdFormatPDF,
    "xml": wpsapi.wdFormatXML,
}


def worker():
    path = "temp_file/out"
    if os.path.exists(path):
        for f in os.listdir(path):
            os.remove(path + "/" + i)
    path = "tem_file/"
    if os.path.exists(path):
        for f in os.listdir(path):
            os.remove(path + "/" + i)

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
hr, app = rpc.getWpsApplication()
if hr != S_OK:
    raise ConvertException("Can't get the application", hr)
app.Visible = False
docs = app.Documents
    
class Myserver(socketserver.BaseRequestHandler):
    def handle(self):
        path = str(self.request.recv(1024), "utf-8").strip()
        new_path = self.convert_to(path, "pdf", False)
        self.request.sendall(bytes(new_path, "utf-8"))
    def convert_to(self, path, format, abort_on_fails=False):
        hr, doc = docs.Open(path, ReadOnly=True)
        out_dir = os.path.dirname(os.path.realpath(path)) + "/out"
        os.makedirs(out_dir, exist_ok=True)
        new_path = out_dir + "/" + os.path.splitext(os.path.basename(path))[0] + "." + format
        doc.SaveAs2(new_path, FileFormat=formats[format])
        doc.Close(wpsapi.wdDoNotSaveChanges)
        return new_path

 
if __name__ == "__main__":
    host, port = "127.0.0.1", 9999
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.ThreadingTCPServer((host, port),Myserver)
    server.serve_forever()
