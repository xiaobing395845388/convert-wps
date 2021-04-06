# coding:utf-8

# * Title: wsserver<br>
# * Description: convert<br>
# * Copyright: Copyright (c) 2019<br>
# * Company: webservice服务端
# * 
# * @author wangbing
# * @date 2021-04-08
# * @version 1.0

import subprocess

from spyne import Application, rpc, ServiceBase
from spyne.model.binary import ByteArray
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
from starlette.responses import FileResponse

from convert import doConvert
from common import clean

class MsWord2PDF(ServiceBase):
    @rpc(ByteArray(min_occurs=1, nullable=False) , _returns=ByteArray)
    def excute(self, file_data):
        return doConvert(file_data, 'pdf')

def start_job():
    result = subprocess.call("curl  --max-time 5 http://127.0.0.1:5678", shell = True)
    if result in [7, 28]:
        subprocess.call("ps -ef|grep wps |awk '{print $2}'|xargs kill -9", shell = True)
        subprocess.call("ps -ef|grep uvicorn |awk '{print $2}'|xargs kill -9", shell = True)
        subprocess.call("uvicorn convert:app --host 0.0.0.0 --port 5678 --log-level error &", shell = True)

application = Application([MsWord2PDF],
                          'spyne.examples.hello',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())
wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    start_job()
    host = '127.0.0.1'
    port = 8000
    server = make_server(host, port, wsgi_application)
    server.serve_forever()
    clean()
