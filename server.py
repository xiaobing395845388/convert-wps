# * Title: server<br>
# * Description: server<br>
# * Copyright: Copyright (c) 2019<br>
# * Company: 华宇（大连）信息服务有限公司<br>
# * 
# * @author wangbing
# * @date 2020-10-10
# * @version 1.0

import os
import sys
import socket

from starlette.requests import Request
from fastapi import FastAPI, Form, File, UploadFile
from starlette.templating import Jinja2Templates
from starlette.responses import FileResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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
    host, port = "127.0.0.1", 9999
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))          # 链接到客户端
        sock.sendall(bytes(path, "utf-8")) # 向服务端发送数据
        new_path = str(sock.recv(1024), "utf-8")# 从服务端接收数据
        return  FileResponse(new_path, filename=file.filename.split(".")[0]+".pdf")
    

