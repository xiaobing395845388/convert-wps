# coding:utf-8

# * Title: docs<br>
# * Description: docs<br>
# * Copyright: Copyright (c) 2019<br>
# * Company: webservice服务端
# * 
# * @author wangbing
# * @date 2021-04-08
# * @version 1.0

import os
import logging

from logging import handlers
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

def work():
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

def clean():
    scheduler = BlockingScheduler()
    scheduler.add_job(work,'cron',day_of_week ='0-6',hour = 0,minute = 0)
    scheduler.add_job(work,'cron',day_of_week ='0-6',hour = 13,minute = 13)
    scheduler.start()

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
