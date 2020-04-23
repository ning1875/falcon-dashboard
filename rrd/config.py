# -*-coding:utf8-*-
# Copyright 2017 Xiaomi, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# app config
import os
import redis
import datetime
from random import Random

# group页面为每个组生成的screen图链接
FALCON_GRP_LINK = "http://yourdashdomain/portal/hostgroup?mine=0&amstag=0"

###end of add


RRD_LOG_PATH = os.environ.get("RRD_LOG_PATH", '/data01/falcon_log/falcon-dash.log')
RRD_LOG_PATH = os.environ.get("RRD_LOG_PATH", 'falcon-dash.log')
LOG_LEVEL = os.environ.get("LOG_LEVEL", 'DEBUG')
SECRET_KEY = os.environ.get("SECRET_KEY", "secret-key")
PERMANENT_SESSION_LIFETIME = os.environ.get("PERMANENT_SESSION_LIFETIME", 3600 * 24 * 30)
SITE_COOKIE = os.environ.get("SITE_COOKIE", "open-falcon-ck")

# Falcon+ API #
API_ADDR = os.environ.get("API_ADDR", "http://yourfalcon-apidomain/api/v1")

# nump
NUMP_DB_HOST = os.environ.get("NUMP_DB_HOST", "")
NUMP_DB_PORT = int(os.environ.get("NUMP_DB_PORT", 3306))
NUMP_DB_USER = os.environ.get("NUMP_DB_USER", "")
NUMP_DB_PASS = os.environ.get("NUMP_DB_PASS", "")
NUMP_DB_NAME = os.environ.get("NUMP_DB_NAME", "r")
# grafana 单机大盘图链接
GRAFANA_HOST_URL = "https://xxx/dashboard/db/openfalcon?orgId=1"
# grafana nump图链接
GRAFANA_NUMP_URL = "https://xxx/d/falcon_poly_metric/falcon_poly_metric?refresh=1m&orgId=1"
# grafana 单一聚合图链接
GRAFANA_SINGLE_POLY_URL = "https://xxx/d/single_metric_falcon_poly_metric/single_metric_falcon_poly_metric?orgId=1"
#
GRAFANA_CLUSTER_URL = "https://xxxx/d/falcon_host_group/falcon_host_group?orgId=1&var-endpoint=All&var-group="
#
GRAFANA_LINK = "https://xxxx/api/dashboards/link"

# grafana api
GRAFANA_URL = "https://xxxx/api/dashboards/db"
GRAFANA_ROOT_BEARER_AUTH_HEADER = {
    "Authorization": "Bearer xxxxx",
    "Content-type": "application/json",
}

JSON_HEADER = {
    "content-type": "application/json"
}

## falcon alarm api list ##
ALARM_ADDRS = [
    ""
]

## end new ##


# portal database
# TODO: read from api instead of db
PORTAL_DB_HOST = os.environ.get("PORTAL_DB_HOST", "xxxxx")
PORTAL_DB_PORT = int(os.environ.get("PORTAL_DB_PORT", 3306))
PORTAL_DB_USER = os.environ.get("PORTAL_DB_USER", "")
PORTAL_DB_PASS = os.environ.get("PORTAL_DB_PASS", "")
PORTAL_DB_NAME = os.environ.get("PORTAL_DB_NAME", "")

UIC_DB_NAME = os.environ.get("UIC_DB_NAME", "uic")

SERVER_SIDE_TOKEN = os.environ.get("SERVER_SIDE_TOKEN", "")
SERVER_SIDE_SALT = os.environ.get("SERVER_SIDE_SALT", "")

# alarm database
# TODO: read from api instead of db
ALARM_DB_HOST = os.environ.get("ALARM_DB_HOST", "")
ALARM_DB_PORT = int(os.environ.get("ALARM_DB_PORT", 3306))
ALARM_DB_USER = os.environ.get("ALARM_DB_USER", "")
ALARM_DB_PASS = os.environ.get("ALARM_DB_PASS", "")
ALARM_DB_NAME = os.environ.get("ALARM_DB_NAME", "")

# ldap config
LDAP_ENABLED = os.environ.get("LDAP_ENABLED", False)
LDAP_SERVER = os.environ.get("LDAP_SERVER", "ldap.forumsys.com:389")
LDAP_BASE_DN = os.environ.get("LDAP_BASE_DN", "dc=example,dc=com")
LDAP_BINDDN_FMT = os.environ.get("LDAP_BINDDN_FMT", "uid=%s,dc=example,dc=com")
LDAP_SEARCH_FMT = os.environ.get("LDAP_SEARCH_FMT", "uid=%s")
LDAP_ATTRS = ["cn", "mail", "telephoneNumber"]
LDAP_TLS_START_TLS = False
LDAP_TLS_CACERTDIR = ""
LDAP_TLS_CACERTFILE = "/etc/openldap/certs/ca.crt"
LDAP_TLS_CERTFILE = ""
LDAP_TLS_KEYFILE = ""
LDAP_TLS_REQUIRE_CERT = True
LDAP_TLS_CIPHER_SUITE = ""

# i18n
BABEL_DEFAULT_LOCALE = 'zh_CN'
BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'
# aviliable translations
LANGUAGES = {
    'en': 'English',
    'zh_CN': 'Chinese-Simplified',
}

# portal site config
MAINTAINERS = ['root']
CONTACT = 'root@open-falcon.org'

# redis
REDIS_HOST = "10.14.68.137"
REDIS_PORT = 6379
# REDIS_PASS = "ff699d1429b9b9180382584cbd91772f"


# group_screen dict
GROUP_SCREEN_DICT = {
    'cpu': 'cpu.busy',
    'mem': 'mem.memused.percent',
    'load': 'load.1min',
    'disk': 'df.bytes.used.percent',
    'net': 'net.if.in.bytes',
}

# skip cas sso url list

# add_default_token_url

ADD_DEFAULT_TOKEN_URL = [
    "/dashboard/tmpgraph",
    "/graph/history",
]


def genrandom_nums(randomlength=10):
    str = ''
    chars = '123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]

    return int(str)


def today_date_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def redis_conn():
    # conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS)
    conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    return conn


from rediscluster import RedisCluster

# redis集群地址
REDIS_CLUSTER_NODES = 'xxxx:7000,xxx:7000'
BASE_IMG_URL = ""


def redis_cluster_conn(startup_nodes=REDIS_CLUSTER_NODES):
    nodes = [{"host": x.split(":")[0], "port": int(x.split(":")[1])} for x in
             startup_nodes.strip().split(',')]
    print(nodes)
    rc = RedisCluster(startup_nodes=nodes, decode_responses=True)
    return rc


try:
    from rrd.local_config import *
except:
    print "[warning] no local config file"
