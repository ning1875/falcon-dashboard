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


__author__ = 'Ulric Qin'

from rrd import app
from rrd import config
from flask import render_template, request, g
from rrd.model.portal.host_group import HostGroup
from rrd.config import redis_conn
import redis
import json

from rrd.utils.logger import logging

log = logging.getLogger(__file__)


def get_user_tag_list(username):
    re_conn = redis_conn()
    re_key = "user_tag_list_%s" % username
    user_tag_list = None
    try:
        user_tag_list = json.loads(re_conn.get(re_key), encoding='utf-8')
        log.info('user:%s,user_tag_list:%s ' % (username, str(user_tag_list)))
    except Exception as e:
        log.error("get_user_tag_list_%s got error:%s" % (username, e))
    return user_tag_list


def format_where_in_str(user_tag_list):
    if not user_tag_list:
        return ""
    in_str = ""
    for i in user_tag_list:
        in_str += "'%s'," % i
    in_str_f = in_str[:-1]
    where = ' AND grp_name IN (%s)' % in_str_f
    return where


def format_where_in_str_FOR_HOME(user_tag_list):
    if not user_tag_list:
        return ""
    in_str = ""
    for i in user_tag_list:
        in_str += "'%s'," % i
    in_str_f = in_str[:-1]
    where = ' grp_name IN (%s)' % in_str_f
    return where


@app.route('/portal/hostgrouptag', methods=["GET", ])
def home_tag_get():
    '''
    这是hostgroup的默认跳转函数
    1.默认amstag=1 mine=0
    :return:
    '''
    page = int(request.args.get('p', 1))
    limit = int(request.args.get('limit', 30))

    user_tag_list = get_user_tag_list(g.user.name)

    query = request.args.get('q', '').strip()
    mine = request.args.get('mine', '0')
    amstag = request.args.get('amstag', '1')

    # amstag==0 说明用户取消了amstag的选择框 所以查询所有的返回
    if amstag == "0":
        me = None
        vs, total = HostGroup.query(page, limit, query, me)
        log.debug(vs)
        return render_template(
            'portal/group/index.html',
            data={
                'vs': vs,
                'total': total,
                'query': query,
                'limit': limit,
                'page': page,
                'mine': mine,
                'amstag': amstag,
                'is_root': g.user.name in config.MAINTAINERS,
            }
        )

    where_in = format_where_in_str_FOR_HOME(user_tag_list)
    vs, total = HostGroup.query_fortag(page, limit, where_in)
    log.debug(vs)
    return render_template(
        'portal/group/index.html',
        data={
            'vs': vs,
            'total': total,
            'query': query,
            'limit': limit,
            'page': page,
            'mine': mine,
            'amstag': amstag,
            'is_root': g.user.name in config.MAINTAINERS,
        }
    )


@app.route('/portal/hostgroup', methods=["GET", ])
def home_get():
    page = int(request.args.get('p', 1))
    limit = int(request.args.get('limit', 30))
    query = request.args.get('q', '').strip()
    mine = request.args.get('mine', '1')
    amstag = request.args.get('amstag', '0')
    me = g.user.name if mine == '1' else None
    vs, total = HostGroup.query(page, limit, query, me)
    log.debug(vs)
    return render_template(
        'portal/group/index.html',
        data={
            'vs': vs,
            'total': total,
            'query': query,
            'limit': limit,
            'page': page,
            'mine': mine,
            'amstag': amstag,
            'is_root': g.user.name in config.MAINTAINERS,
        }
    )


def format_common_where_in_str(args):
    if not args:
        return ""
    in_str = ""
    for i in args:
        in_str += "'%s'," % i
    in_str_f = in_str[:-1]
    where = '  IN (%s)' % in_str_f
    return where
