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
## non-docker
- Python 3.5+
- Qt5 
- WPS Office for Linux 11.1.0.9080+
- sip 5.0
- qmake
- g++
- desktop env
```
python3 convert.py & uvicorn server:app --host 0.0.0.0 --port 5678  --workers 8
```
## docker
docker run -it  -p 5678:5678  registry.thunisoft.com:5000/thunisoft/onlinepaper:1.1

