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
import subprocess

#from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

base_path = "/headless/temp_file" 

def clean():
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
def health():
    result = subprocess.call("curl  --max-time 5 http://127.0.0.1:5678", shell = True)
    if result in [7, 28]:
        subprocess.call("ps -ef|grep wps |awk '{print $2}'|xargs kill -9", shell = True)
        subprocess.call("ps -ef|grep uvicorn |awk '{print $2}'|xargs kill -9", shell = True)
        subprocess.call("uvicorn convert:app --host 0.0.0.0 --port 5678 --log-level error &", shell = True)

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(clean,'cron',day_of_week ='0-6',hour = 0,minute = 0)
    scheduler.add_job(clean,'cron',day_of_week ='0-6',hour = 13,minute = 13)
    scheduler.add_job(health,'interval',seconds = 10)
    scheduler.start()