# coding=utf-8
from apscheduler.schedulers.blocking import BlockingScheduler

from app_op import *
from notify import *

logging.basicConfig(level=logging.ERROR)

# 钉钉的Webhook地址

dingUrl = 'https://oapi.dingtalk.com/robot/send?access_token='

# 监控的应用列表
monitor_apps = get_monitor_apps()

# 影响的应用
effect_apps = get_effect_apps(monitor_apps)

# 监控标记，避免重复提醒
monitor_flag = {}


# 获取被影响应用
def get_effect_apps_str(apps, app_name):
    apps_str = ""

    if apps.get(app_name) is not None and len(apps[app_name]) > 0:
        for app in apps[app_name]:
            if apps_str == "":
                apps_str += app
            else:
                apps_str += ", " + app

    return apps_str


# 访问链接
def get_url_resp(app_url):
    try:
        resp = requests.get(app_url, timeout=20)
    except:
        return False
    else:
        return resp


# 监控链接状态
def monitor_url_connect(app, url):
    if monitor_flag.get(url) is None:
        monitor_flag[url] = False

    resp = get_url_resp(url)

    if resp is False:
        resp = get_url_resp(url)

    if resp is False:
        if monitor_flag[url] is False:
            monitor_flag[url] = True
            error_notify(app, "无法访问", get_effect_apps_str(effect_apps, app.name), dingUrl)
    elif resp.status_code != 200 and resp.status_code not in app.ignore:
        if monitor_flag[url] is False:
            monitor_flag[url] = True
            error_notify(app, resp.status_code, get_effect_apps_str(effect_apps, app.name), dingUrl)
    else:
        if monitor_flag[url]:
            recover_notify(app, dingUrl)
        monitor_flag[url] = False

    return resp


# # 监控 SpringBoot 应用 /info
# def monitor_app_info(app):
#     resp = requests.get(app.url + "/info", timeout=10)
#
#     if not resp:
#         return False
#
#     app_info = json.loads(resp.text)
#     app_name = ""
#
#     if app_info.get('app') is not None and app_info['app'].get('name') is not None:
#         app_name = app_info['app']['name']
#
#     return app_name


# 监控 SpringBoot 应用所使用的服务的状态
def monitor_app_service_status(app, app_health, app_service_type):
    if app_health.get(app_service_type) is None:
        return False

    app_service = app_health[app_service_type]

    if monitor_flag.get(app.name + app_service_type) is None:
        monitor_flag[app.name + app_service_type] = False

    if app_service['status'] == 'DOWN':
        if monitor_flag[app.name + app_service_type] is False:
            monitor_flag[app.name + app_service_type] = True
            warn_notify(app, app_service_type + " 当前状态：" + app_service['status'], dingUrl)
    else:
        if monitor_flag[app.name + app_service_type]:
            recover_notify(app, dingUrl, "使用的 " + app_service_type + " 恢复正常")
        monitor_flag[app.name + app_service_type] = False


# 监控 SpringBoot 应用 /health
def monitor_app_health(app):
    resp = monitor_url_connect(app, app.url + "/health")

    if resp is False:
        return False

    app_health = json.loads(resp.text)

    # app_status = app_health['status']

    # if app_status is not None and app_status == 'DOWN':
    #     warn_notify(app, "当前状态：" + app_status, dingUrl)

    if app_health.get('diskSpace') is not None:
        app_disk_space = app_health['diskSpace']

        if monitor_flag.get(app.name + 'diskSpace') is None:
            monitor_flag[app.name + 'diskSpace'] = False

        if app_disk_space.get('free') is not None and app_disk_space.get('total') is not None:
            if app_disk_space['free'] / app_disk_space['total'] <= 0.05:
                if monitor_flag[app.name + 'diskSpace'] is False:
                    monitor_flag[app.name + 'diskSpace'] = True
                    warn_notify(app, "磁盘空间不足 5%，当前剩余 " + str(round(app_disk_space['free'] / 1073741824, 2)) + "GB",
                                dingUrl)
            else:
                monitor_flag[app.name + 'diskSpace'] = False

    monitor_app_service_status(app, app_health, 'redis')
    monitor_app_service_status(app, app_health, 'db')


# 监控 SpringBoot 应用 /metrics
def monitor_app_metrics(app):
    resp = monitor_url_connect(app, app.url + "/metrics")

    if resp is False or resp.status_code != 200:
        return False

    app_metrics = json.loads(resp.text)

    if app_metrics.get('mem') is not None and app_metrics.get('mem.free') is not None:
        app_mem = app_metrics['mem']
        app_mem_fee = app_metrics['mem.free']

        if monitor_flag.get(app.name + 'mem') is None:
            monitor_flag[app.name + 'mem'] = False

        if app_mem_fee / app_mem <= 0.1:
            if not monitor_flag[app.name + 'mem']:
                monitor_flag[app.name + 'mem'] = True
                warn_notify(app, "内存不足 10%，当前剩余 " + str(round(app_mem_fee / 1024, 2)) + "MB", dingUrl)
        else:
            monitor_flag[app.name + 'mem'] = False


# 监控应用
def monitor():
    for app in monitor_apps:

        if app.type == AppType.Normal:
            monitor_url_connect(app, app.url)

        elif app.type == AppType.SpringBoot:
            monitor_app_health(app)
            monitor_app_metrics(app)


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(monitor, 'cron', second='*/10', hour='*')

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
