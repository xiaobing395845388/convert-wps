# * Title: convert<br>
# * Description: convert<br>
# * Copyright: Copyright (c) 2019<br>
# * Company: »ªÓî£¨´óÁ¬£©ÐÅÏ¢·þÎñÓÐÏÞ¹«Ë¾<br>
# * 
# * @author wangbing
# * @date 2020-10-10
# * @version 1.0

import os
import sys
import subprocess

import logging

from apscheduler.schedulers.blocking import BlockingScheduler

base_path = "/headless/temp_file" 

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

def clean():
    path = base_path + "/out"
    if os.path.exists(path):
        for f in os.listdir(path):
            try:
                os.remove(path + "/" + f)
            except IOError:
                print("Error: 没有找到文件或读取文件失败" + path + "/" + f)
                logger.error("Error: 没有找到文件或读取文件失败%s" % path + "/" + f)
    if os.path.exists(base_path):
        for f in os.listdir(base_path):
            file_path = base_path + "/" + f
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except IOError:
                    print("Error: 没有找到文件或读取文件失败" + file_path)
                    logger.error("Error: 没有找到文件或读取文件失败%s" % file_path)
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