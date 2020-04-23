# -*- coding:utf-8 -*-
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


import json
import requests
import math
from flask import g, redirect, session, abort, request
from requests.adapters import HTTPAdapter
from functools import wraps
from rrd import config
from rrd import corelib
from rrd.model.user import User, UserToken
from rrd.config import SERVER_SIDE_TOKEN, \
    SERVER_SIDE_SALT, \
    GRAFANA_ROOT_BEARER_AUTH_HEADER, \
    GRAFANA_URL, \
    JSON_HEADER
from rrd.utils.logger import logging

log = logging.getLogger(__file__)


def remote_ip():
    if not request.headers.getlist("X-Forward-For"):
        return request.remote_addr
    else:
        return request.headers.getlist("X-Forward-For")[0]


def require_login(redir="/auth/login"):
    def _(f):
        @wraps(f)
        def __(*a, **kw):
            if not g.user:
                return redirect(redir or "/auth/login")
            return f(*a, **kw)

        return __

    return _


def require_login_abort(status_code=403, msg="login first"):
    def _(f):
        @wraps(f)
        def __(*a, **kw):
            if not g.user:
                return abort(status_code, msg)
            return f(*a, **kw)

        return __

    return _


def require_login_json(json_msg={"ok": False, "msg": "login first"}):
    def _(f):
        @wraps(f)
        def __(*a, **kw):
            if not g.user:
                return json.dumps(json_msg)
            return f(*a, **kw)

        return __

    return _


def set_user_cookie(user_token, session_):
    if not user_token:
        return None

    session_[config.SITE_COOKIE] = "%s:%s" % (user_token.name, user_token.sig)
    log.debug("set_user_cookie :%s" % str(session_))


def clear_user_cookie(session_):
    session_[config.SITE_COOKIE] = ""


def get_usertoken_from_session(session_):
    if config.SITE_COOKIE in session_:
        cookies = session_[config.SITE_COOKIE]
        if not cookies:
            return None

        name, sig = cookies.split(":")
        return UserToken(name, sig)


def get_current_user_profile(user_token):
    # log.debug("get_current_user_profile_%s"%str(user_token))
    if not user_token:
        return

        # red = redis_conn()
    #
    # sig_expired=3600*24*30
    # red_key="user_sig_%s"%user_token.name
    # log.debug("get_redis_key:%s"%red_key)
    # res=None
    # try:
    #   res = json.loads(red.get(red_key))
    # except Exception as e:
    #    log.error("get_current_user_profile_from_redis got error",e)
    # if not res:
    #    return

    h = {"Content-type": "application/json"}
    r = corelib.auth_requests("GET", "%s/user/current/" % (config.API_ADDR), headers=h, )
    if r.status_code != 200:
        return

    j = r.json()
    return User(j["id"], j["name"], j["cnname"], j["email"], j["phone"], j["im"], j["qq"], j["role"])


def logout_user(user_token):
    if not user_token:
        return

    r = corelib.auth_requests("GET", "%s/user/logout" % config.API_ADDR)
    if r.status_code != 200:
        raise Exception("%s:%s" % (r.status_code, r.text))
    clear_user_cookie(session)


def login_user(name, password):
    log.debug("call_login_user %s" % name)

    params = {
        "name": name,
        "password": password,
        "admin_salt": SERVER_SIDE_SALT
    }

    r = requests.post("%s/user/login" % config.API_ADDR, data=params)
    if r.status_code == 400:
        if 'no such user' in r.json().get('error'):
            # need to create_user
            data = {
                "name": name,
                "password": name,
                "email": "%s@xxxx.com" % name,
                "cnname": name}
            headers = {
                "Apitoken": json.dumps({"name": "root", "sig": SERVER_SIDE_TOKEN}),
                "Content-type": "application/json"
            }
            r_create = requests.post("%s/user/create" % (config.API_ADDR,), headers=headers, data=json.dumps(data), )
            if r_create.status_code == 200:
                log.debug("successfully_create_user %s" % name)
                r = r_create
            else:
                log.error("error_create_user:status_code:%s %s ,%s" % (r_create.status_code, name, r_create.text))
                raise Exception("%s : %s" % (r_create.status_code, r_create.text))

    if r.status_code != 200:
        raise Exception("%s : %s" % (r.status_code, r.text))

    j = r.json()
    ut = UserToken(j["name"], j["sig"])
    set_user_cookie(ut, session)
    return ut


def create_user(name, password, cname, email, phone):
    h = {"Content-type": "application/json"}
    d = {
        "name": name,
        "password": password,
        "cnname": cname,
        "email": email,
        "phone": phone,
    }

    r = requests.post("%s/user/create" % (config.API_ADDR,), \
                      data=json.dumps(d), headers=h)


def ldap_login_user(name, password):
    import ldap
    if not config.LDAP_ENABLED:
        raise Exception("ldap not enabled")

    bind_dn = config.LDAP_BINDDN_FMT
    base_dn = config.LDAP_BASE_DN
    try:
        bind_dn = config.LDAP_BINDDN_FMT % name
    except TypeError:
        pass

    search_filter = config.LDAP_SEARCH_FMT
    try:
        search_filter = config.LDAP_SEARCH_FMT % name
    except TypeError:
        pass

    cli = None
    try:
        ldap_server = config.LDAP_SERVER if (config.LDAP_SERVER.startswith("ldap://") or config.LDAP_SERVER.startswith(
            "ldaps://")) else "ldaps://%s" % config.LDAP_SERVER if config.LDAP_TLS_START_TLS else "ldap://%s" % config.LDAP_SERVER
        log.debug("ldap_server:%s bind_dn:%s base_dn:%s filter:%s attrs:%s" % (
        ldap_server, bind_dn, config.LDAP_BASE_DN, search_filter, config.LDAP_ATTRS))
        cli = ldap.initialize(ldap_server)
        cli.protocol_version = ldap.VERSION3
        if config.LDAP_TLS_START_TLS or ldap_server.startswith('ldaps://'):
            if config.LDAP_TLS_CACERTFILE:
                cli.set_option(ldap.OPT_X_TLS_CACERTFILE, config.LDAP_TLS_CACERTFILE)
            if config.LDAP_TLS_CERTFILE:
                cli.set_option(ldap.OPT_X_TLS_CERTFILE, config.LDAP_TLS_CERTFILE)
            if config.LDAP_TLS_KEYFILE:
                cli.set_option(ldap.OPT_X_TLS_KEYFILE, config.LDAP_TLS_KEYFILE)
            if config.LDAP_TLS_REQUIRE_CERT:
                cli.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, config.LDAP_TLS_REQUIRE_CERT)
            if config.LDAP_TLS_CIPHER_SUITE:
                cli.set_option(ldap.OPT_X_TLS_CIPHER_SUITE, config.LDAP_TLS_CIPHER_SUITE)
        cli.simple_bind_s(bind_dn, password)
        result = cli.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter, config.LDAP_ATTRS)
        log.debug("ldap result: %s" % result)
        d = result[0][1]
        email = d['mail'][0]
        cnname = d['cn'][0]
        if 'sn' in d and 'givenName' in d:
            cnname = d['givenName'][0] + ' ' + d['sn'][0]
        if 'displayName' in d:
            cnname = d['displayName'][0]
        if 'telephoneNumber' in d:
            phone = d['telephoneNumber'] and d['telephoneNumber'][0] or ""
        else:
            phone = ""

        return {
            "name": name,
            "password": password,
            "cnname": cnname,
            "email": email,
            "phone": phone,
        }
    except ldap.LDAPError as e:
        cli and cli.unbind_s()
        raise e
    except (IndexError, KeyError) as e:
        raise e
    finally:
        cli and cli.unbind_s()





def create_grafana(grp_name, svs_name):
    """create grafana graph, show hostgroup and service option for proc argus"""
    grafana_json = create_grafana_json(grp_name, svs_name)
    res = base_requests("POST", GRAFANA_URL, headers=GRAFANA_ROOT_BEARER_AUTH_HEADER, data=json.dumps(grafana_json))

    if res.status_code != 200:
        log.error("Create grafana for proc agrus error: %s, %s" % (res.status_code, res.text))
        return 'Create grafana for proc agrus fail'
    return ''


def create_grafana_json(grp_name, svs_name):
    name = "hostgroup_%s" % grp_name
    flame_url = "http://perfana.10.23.123.12.nip.io/flamegraph/?hostgroup=%s&service=%s" \
                % (grp_name, svs_name)
    templating = create_templates(grp_name, svs_name)
    panels = create_panels()

    base = {
        "annotations": {
            "list": [
                {
                    "builtIn": 1,
                    "datasource": "-- Grafana --",
                    "enable": True,
                    "hide": True,
                    "iconColor": "rgba(0, 211, 255, 1)",
                    "name": "Annotations & Alerts",
                    "type": "dashboard"
                }
            ]
        },
        "editable": True,
        "gnetId": None,
        "graphTooltip": 0,
        "id": None,
        "iteration": 1557058481507,
        "links": [
            {
                "icon": "external link",
                "includeVars": True,
                "keepTime": True,
                "tags": [

                ],
                "targetBlank": True,
                "title": "Perfana Flamegraph",
                "tooltip": "Open Perfana Flamegraph Dashboard",
                "type": "link",
                "url": flame_url
            }
        ],
        "panels": panels,
        "refresh": False,
        "schemaVersion": 16,
        "style": "dark",
        "tags": [

        ],
        "templating": templating,
        "time": {
            "from": "now-6h",
            "to": "now"
        },
        "timepicker": {
            "refresh_intervals": [
                "5s",
                "10s",
                "30s",
                "1m",
                "5m",
                "15m",
                "30m",
                "1h",
                "2h",
                "1d"
            ],
            "time_options": [
                "5m",
                "15m",
                "1h",
                "6h",
                "12h",
                "24h",
                "2d",
                "7d",
                "30d"
            ]
        },
        "timezone": "",
        "title": name,
        "uid": None,
        "version": 1,
    }

    fjson = {
        "dashboard": base,
        "overwrite": True,
    }
    return fjson


def create_panels():
    # create panels
    panels = []
    pid = 1

    # create proc.cpu
    cpus = ["use", "utime", "stime", "cstime", "cutime"]
    for metric in cpus:
        title = "proc.cpu.%s" % metric
        target = "$host_group_name#proc#cpu#%s/service=$service_name" % metric
        panels.append(create_single_panel(title, target, pid))
        pid = pid + 1

    # create proc.mem
    mems = ["peak", "size", "lck", "hwm", "rss", "data", "stk", "exe", "lib", "pte", "swap"]
    for metric in mems:
        title = "proc.mem.%s" % metric
        target = "$host_group_name#proc#mem#%s/service=$service_name" % metric
        panels.append(create_single_panel(title, target, pid))
        pid = pid + 1

    # create proc.net
    nets = ["tcp_send", "tcp_recv", "udp_send", "udp_recv"]
    for metric in nets:
        title = "proc.net.%s" % metric
        target = "$host_group_name#proc#net#%s/service=$service_name" % metric
        panels.append(create_single_panel(title, target, pid))
        pid = pid + 1

    # create proc.ss.toplat from top1 to top10
    title = "proc.ss.toplat"
    target = "$host_group_name#proc#ss#toplat/service=$service_name"
    panels.append(create_single_panel(title, target, pid))

    return panels


def create_single_panel(title, target, pid):
    """create one panel for one metric"""
    x = 0
    y = 0
    if pid % 2 == 0:
        x = 12
        tmppid = pid
    else:
        x = 0
        tmppid = pid + 1
    calnum = int(math.ceil(tmppid / 2))
    ducenum = int(math.floor(tmppid / 2 / 9))
    y = (calnum % 9 - 1 + ducenum * 9) * 9

    panel_template = {
        "aliasColors": {

        },
        "bars": False,
        "dashLength": 10,
        "dashes": False,
        "datasource": "falcon",
        "fill": 0,
        "gridPos": {
            "h": 9,
            "w": 12,
            "x": 0,
            "y": 0
        },
        "id": pid,
        "legend": {
            "avg": False,
            "current": False,
            "max": False,
            "min": False,
            "show": True,
            "total": False,
            "values": False
        },
        "lines": True,
        "linewidth": 1,
        "links": [

        ],
        "nullPointMode": "null",
        "percentage": False,
        "pointradius": 5,
        "points": False,
        "renderer": "flot",
        "seriesOverrides": [

        ],
        "spaceLength": 10,
        "stack": False,
        "steppedLine": False,
        "targets": [
            {
                "aggregator": "sum",
                "downsampleAggregator": "avg",
                "downsampleFillPolicy": "none",
                "refId": "B",
                "target": "$host_group_name#proc#ss#toplat/service=$service_name,top=2",
                "textEditor": True
            }
        ],
        "thresholds": [

        ],
        "timeFrom": None,
        "timeShift": None,
        "title": "proc.ss.toplat.top2",
        "tooltip": {
            "shared": True,
            "sort": 0,
            "value_type": "individual"
        },
        "type": "graph",
        "xaxis": {
            "buckets": None,
            "mode": "time",
            "name": None,
            "show": True,
            "values": [

            ]
        },
        "yaxes": [
            {
                "format": "short",
                "label": None,
                "logBase": 1,
                "max": None,
                "min": None,
                "show": True
            },
            {
                "format": "short",
                "label": None,
                "logBase": 1,
                "max": None,
                "min": None,
                "show": True
            }
        ],
        "yaxis": {
            "align": False,
            "alignLevel": None
        }
    }

    panel_template["title"] = title
    panel_template["targets"][0]["target"] = target
    panel_template["gridPos"]["x"] = x
    panel_template["gridPos"]["y"] = y
    return panel_template


def create_templates(grp_name, svs_name):
    """create template for graph"""
    svs_names = svs_name.split(",")
    template_options = []
    for svs_name_single in svs_names:
        one_option = {
            "selected": True,
            "text": svs_name_single,
            "value": svs_name_single
        }
        template_options.append(one_option)
    templating = {
        "list": [
            {
                "allValue": None,
                "current": {

                },
                "datasource": "falcon",
                "hide": 0,
                "includeAll": True,
                "label": None,
                "multi": True,
                "name": "host_group_name",
                "options": [

                ],
                "query": "!HGH!%s" % grp_name,
                "refresh": 1,
                "regex": "",
                "sort": 0,
                "tagValuesQuery": "",
                "tags": [

                ],
                "tagsQuery": "",
                "type": "query",
                "useTags": True
            },
            {
                "allValue": None,
                "current": {
                    "tags": [

                    ],
                    "text": svs_names[0],
                    "value": svs_names[0]
                },
                "hide": 0,
                "includeAll": False,
                "label": None,
                "multi": False,
                "name": "service_name",
                "options": template_options,
                "query": svs_name,
                "type": "custom"
            }
        ]
    }
    return templating


def base_requests(method, *args, **kwargs):
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=3))
    s.mount('https://', HTTPAdapter(max_retries=3))

    headers = {}
    if not kwargs:
        kwargs = {}

    if "headers" in kwargs:
        headers.update(kwargs["headers"])
        del kwargs["headers"]

    g_timeout = 5
    if "timeout" not in kwargs:
        kwargs["timeout"] = g_timeout
    if method == "POST":
        return requests.post(*args, headers=headers, **kwargs)
    elif method == "GET":
        return requests.get(*args, headers=headers, **kwargs)
    elif method == "PUT":
        return requests.put(*args, headers=headers, **kwargs)
    elif method == "DELETE":
        return requests.delete(*args, headers=headers, **kwargs)
    else:
        raise Exception("invalid http method")
