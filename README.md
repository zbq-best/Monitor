# Monitor

基于Python 的应用监控程序

## 作者

木白

## 如何使用

1. 下载源码
2. 修改 app.json (监控的应用列表)
3. 修改 finance_monitor.py 中的 dingUrl (钉钉机器人的webhook)
4. 运行 finance_monitor.py

## 如何修改定时

修改 `finance_monitor.py` 里的 `scheduler.add_job(monitor, 'cron', second='*/10', hour='*')`

## 监控范围

- 普通应用：监控链接是否能够访问，链接状态码
- Spring Boot应用：监控 /health 中的磁盘空间和服务状态，/metrics 中的内存

## app.json 结构说明

```
{
  "appName": "app",                   //应用名称
  "appUrl": "http://localhost:8080",  //监控链接
  "appType": 1,                       //应用类型 (0.普通应用 1.Spring Boot应用)
  "owner": ["1234567890"],            //应用负责人，异常时钉钉需要@的人
  "ignore": [404],                    //忽略的状态码，忽略404时，当应用监控链接404时不触发警报
  "rely": ["ABC"]                     //依赖的其他应用名称
}
```
