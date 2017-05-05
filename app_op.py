# coding=utf-8
import json

from enum import Enum, unique


@unique
class AppType(Enum):
    Normal = 0
    SpringBoot = 1


app_types = [AppType.Normal, AppType.SpringBoot]


class App:
    def __init__(self, app_json):
        self.name = app_json['appName']
        self.url = app_json['appUrl']
        self.type = app_types[app_json['appType']]
        self.owner = app_json['owner']

        if app_json.get('ignore') is not None:
            self.ignore = app_json['ignore']
        else:
            self.ignore = []

        if app_json.get('rely') is not None:
            self.rely = app_json['rely']
        else:
            self.rely = []


def load_app_json():
    f = open("app.json", encoding='utf-8')
    return json.load(f)


def get_monitor_apps():
    apps = load_app_json()

    monitor_apps = list()

    for app_json in apps:
        if app_json.get('appUrl') is None or app_json.get('appType') is None:
            continue
        monitor_apps.append(App(app_json))

    return monitor_apps


def get_effect_apps(apps):
    effect_apps = {}

    for app in apps:
        if len(app.rely) > 0:
            for rely_app in app.rely:
                if effect_apps.get(rely_app) is None:
                    effect_apps[rely_app] = list()

                effect_apps[rely_app].append(app.name)

    return effect_apps


if __name__ == '__main__':
    pass
