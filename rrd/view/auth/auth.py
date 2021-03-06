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

from rrd.flask_cas import login_required

from flask import request, g, abort, render_template, redirect, session, url_for
from flask_babel import refresh
import requests
import json
from rrd import app
from rrd import config
from rrd.model.user import User
from rrd.view import utils as view_utils

from rrd.utils.logger import logging

log = logging.getLogger(__file__)


# @login_required
@app.route("/auth/login", methods=["GET", "POST"])
def auth_login():
    # log.debug("auth_login_called_show_session %s",str(session))

    ret = {"msg": "", }
    try:
        user_info = session['CAS_ATTRIBUTES']
        username = session['CAS_USERNAME']
        email = user_info['cas:email']
        cname = user_info['cas:full_name']
        phone = ''
        print user_info, username, email, cname, phone
        h = {"Content-type": "application/json"}
        d = {
            "name": username,
            "password": username,
            "cnname": cname,
            "email": email,
            "phone": "",
        }
        # 这个 login_user正常只会运行一次 ,通过api get redis拿到token 后 做session判断就不会再次调用这里了
        ut = view_utils.login_user(username, username)
        log.debug("ut_called", str(ut))
        if not ut:
            ret["msg"] = "no such user"
            return json.dumps(ret)
        ret["data"] = {
            "name": ut.name,
            "sig": ut.sig,
        }
        # return json.dumps(ret)
        log.debug("request.args.get('next')", request.args.get('next'))
        # redirect_url = session.get('CAS_AFTER_LOGIN_SESSION_URL',None)
        redirect_url = session.get('CAS_AFTER_LOGIN',None)
        # print("3",redirect_url,session)
        # return redirect(request.args.get('next') or url_for('index'))
        return redirect(redirect_url or url_for('index'))
    except Exception as e:
        ret["msg"] = str(e)
        return json.dumps(ret)

    # if request.method == "GET":
    #    if g.user:
    #        return redirect("/")
    #
    #    return render_template("auth/login.html", **locals())
    # if request.method == "POST":
    #    ret = { "msg": "", }
    #
    #    name = request.form.get("name")
    #    password = request.form.get("password")
    #    ldap = request.form.get("ldap") or "0"

    #    if not name or not password:
    #        ret["msg"] = "no name or password"
    #        return json.dumps(ret)
    #
    #    if ldap == "1":
    #        try:
    #            ldap_info = view_utils.ldap_login_user(name, password)
    #
    #            h = {"Content-type":"application/json"}
    #            d = {
    #                "name": name,
    #                "password": password,
    #                "cnname": ldap_info['cnname'],
    #                "email": ldap_info['email'],
    #                "phone": ldap_info['phone'],
    #            }
    #
    #            r = requests.post("%s/user/create" %(config.API_ADDR,), \
    #                    data=json.dumps(d), headers=h)
    #            log.debug("%s:%s" %(r.status_code, r.text))
    #
    #            #TODO: update password in db if ldap password changed
    #       except Exception as e:
    #           ret["msg"] = str(e)
    #           return json.dumps(ret)
    #
    #   try:
    #       ut = view_utils.login_user(name, password)
    #       if not ut:
    #           ret["msg"] = "no such user"
    #           return json.dumps(ret)
    #
    #       ret["data"] = {
    #               "name": ut.name,
    #               "sig": ut.sig,
    #       }
    #       return json.dumps(ret)
    #   except Exception as e:
    #       ret["msg"] = str(e)
    #       return json.dumps(ret)


@app.route("/auth/logout", methods=["GET", ])
def auth_logout():
    if request.method == "GET":
        view_utils.logout_user(g.user_token)
        return redirect("/auth/login")


@app.route("/auth/register", methods=["GET", "POST"])
def auth_register():
    if request.method == "GET":
        if g.user:
            return redirect("/auth/login")
        return render_template("auth/register.html", **locals())

    if request.method == "POST":
        ret = {"msg": ""}

        name = request.form.get("name", "")
        cnname = request.form.get("cnname", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        repeat_password = request.form.get("repeat_password", "")

        if not name or not password or not email or not cnname:
            ret["msg"] = "not all form item entered"
            return json.dumps(ret)

        if password != repeat_password:
            ret["msg"] = "repeat password not equal"
            return json.dumps(ret)

        h = {"Content-type": "application/json"}
        d = {
            "name": name,
            "cnname": cnname,
            "email": email,
            "password": password,
        }

        r = requests.post("%s/user/create" % (config.API_ADDR,), \
                          data=json.dumps(d), headers=h)
        log.debug("%s:%s" % (r.status_code, r.text))

        if r.status_code != 200:
            ret['msg'] = r.text

        return json.dumps(ret)
