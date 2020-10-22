# install

```
pip3 install python-multipart
pip3 install jinja2 
pip3 install aiofiles
pip3 install pywpsrpc -i https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install fastapi
pip3 install uvicorn
```
# run 
```
nohup uvicorn convert:app --host 0.0.0.0 --port 5678  --workers 8
```

