# -*- coding:utf-8 -*-
# Copyright 2019 xxxxx, Inc.
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
import requests
import json
import pdb
import math
from .bean import Bean
from .template import Template
from .host_group import HostGroup

class GrpSvs(Bean):
    _tbl = 'grp_svs'
    _cols = 'id, grp_id, grp_name, svs_name, bind_user, isflame, finterval, fduration'
    _max_obj_items = 5
    _max_obj_len = 1024

    def __init__(self, id, grp_id, grp_name, svs_name, bind_user, isflame, finterval, fduration):
        self.id = id 
        self.grp_id = grp_id
        self.grp_name = grp_name
        self.svs_name = svs_name
        self.isflame = isflame
        self.finterval = finterval
        self.fduration = fduration
        self.bind_user = bind_user

    @classmethod
    def query(cls, page, limit, query, me=None):
        where = ''
        params = []

        if me is not None:
            where = 'bind_user = %s'
            params.append(me)

        if query:
            where += ' and ' if where else ''
            where += ' svs_name like %s'
            params.append('%' + query + '%')

        vs = cls.select_vs(where=where, params=params, page=page, limit=limit)
        total = cls.total(where=where, params=params)
        return vs, total

    @classmethod
    def save_or_update(cls, s_id, g_name, s_name, login_user, isflame, finterval, fduration):
        g_ids = HostGroup.column('id', where='grp_name=%s', params=[g_name])
        if not g_ids:
            return "no group named %s" % g_name

        if len(g_ids) > 1:
            return "replicated group name %s" % g_name

        g_id = g_ids[0]

        if not isflame:
            isflame = 0

        if s_id:
            return cls.update_service(s_id, g_id, g_name, s_name, login_user, isflame, finterval, fduration)
        else:
            return cls.insert_service(g_id, g_name, s_name, login_user, isflame, finterval, fduration)

    @classmethod
    def insert_service(cls, g_id, g_name, s_name, login_user, isflame, finterval, fduration):

        raw_sql = "select * from {} where grp_id='{}'".format(cls._tbl, g_id)
        res = cls._db.query_all(raw_sql)
        if len(res) > 0:
            return "grp_name='{}' and svs_name='{}' and bind_user='{}' exist".format(g_name, s_name, login_user)

        s_id = GrpSvs.insert({
            'grp_id':       g_id,
            'grp_name':     g_name,
            'svs_name':     s_name,
            'bind_user':    login_user,
            'isflame':      isflame,
            'finterval':    finterval,
            'fduration':    fduration,
        })

        if s_id:
            return ''

        return 'save service fail'

    @classmethod
    def update_service(cls, s_id, g_id, g_name, s_name, login_user, isflame, finterval, fduration):
        e = GrpSvs.get(s_id)
        if not e:
            return 'no such nodata config %s' % s_id

        GrpSvs.update_dict(
            {
                'grp_id':       g_id,
                'grp_name':     g_name,
                'svs_name':     s_name,
                'bind_user':    login_user,
                'isflame':      isflame,
                'finterval':    finterval,
                'fduration':    fduration,
            },
            'id=%s',
            [e.id]
        )
        return ''

    def writable(self, login_user):
        # login_user can be str or User obj
        if isinstance(login_user, str):
            login_user = User.get_by_name(login_user)

        if not login_user:
            return False

        if login_user.is_admin() or login_user.is_root():
            return True

        if self.bind_user == login_user.name:
            return True

        return False
