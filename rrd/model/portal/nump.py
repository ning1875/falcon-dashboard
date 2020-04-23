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


from .bean import Bean
from rrd.store import num_db


class Nump(Bean):
    _db = num_db
    _tbl = 'grp_outlier'
    _cols = 'id, grp_name, counter, timestamp, value, create_at'

    def __init__(self, id, grp_name, counter, timestamp, value, create_at):
        self.id = id
        self.grp_name = grp_name
        self.counter = counter
        self.timestamp = timestamp
        self.value = value
        self.create_at = create_at

    @classmethod
    def query_list(cls, page, limit, grp_name_list):
        if grp_name_list:
            where = 'grp_name in ({})'
            str = ""

            for s in grp_name_list:
                str += "'{}',".format(s)
            str = str[:-1]
            where = where.format(str)
        else:
            where = ""

        params = []

        vs = cls.select_vs(where=where, params=params, page=page, limit=limit, order='timestamp desc')
        total = cls.total(where, params)

        return vs, total

