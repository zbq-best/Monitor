#coding=utf-8
import json
import logging
import time

import requests


# 发送钉钉提醒
def ding_notify(url, content):
    headers = {"Content-Type": "application/json"}
    requests.post(url, data=json.dumps(content), headers=headers)


# 应用异常提醒
def error_notify(app, status, effect, ding_url):
    if effect != "":
        effect = " \n > \n > 影响：" + effect

    content = {
        "msgtype": "markdown",
        "markdown": {
            "title": app.name + " 异常",
            "text": "### " + app.name + " 异常\n > \n > 状态：**" + str(status) + "** \n > \n > 监控：" + app.url + effect
        }
    }
    ding_notify(ding_url, content)
    owner_notify(app, ding_url)
    logging.error("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]\t" + app.name + " " + str(status))


# 应用告警
def warn_notify(app, text, ding_url):
    content = {
        "msgtype": "markdown",
        "markdown": {
            "title": app.name + " 告警",
            "text": "### " + app.name + " 告警\n > \n > " + text
        }
    }
    ding_notify(ding_url, content)
    owner_notify(app, ding_url)
    logging.error("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]\t" + app.name + " " + text)


# 应用恢复提醒
def recover_notify(app, ding_url, text="恢复正常"):
    content = {
        "msgtype": "markdown",
        "markdown": {
            "title": app.name + " " + text,
            "text": "### " + app.name + " " + text + "\n > \n > 监控：" + app.url
        }
    }
    ding_notify(ding_url, content)
    logging.error("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]\t" + app.name + " " + text)


# 应用负责人提醒
def owner_notify(app, ding_url, text="请及时处理"):
    if len(app.owner):
        content = {
            "msgtype": "text",
            "text": {
                "content": text
            },
            "at": {
                "atMobiles": app.owner,
                "isAtAll": False
            }
        }
        ding_notify(ding_url, content)