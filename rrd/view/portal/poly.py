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


__author__ = 'niean'
from rrd import app
from flask import request, g, render_template, jsonify
from rrd.model.portal.poly import PolyMetric
from rrd.utils.params import required_chk
from rrd.utils.logger import logging
from rrd.utils.format import replace_str_for_counter
from rrd.config import *
log = logging.getLogger(__file__)


def gen_single_poly_grafana_link(grp_p, metric_p):
    '''

    https://grafana.xxxx.com/d/single_metric_falcon_poly_metric/single_metric_falcon_poly_metric?orgId=1
    &refresh=1m&var-metric_line=cpu_busy&var-metric=cpu.busy
    &var-poly_res_sum=poly_res_cpu_busy_sum&var-poly_res_avg=poly_res_cpu_busy_avg
    # &&var-falcon_poly_name=falcon_group_poly_data_system_openfalcon
    # &var-grp_name=data_system_openfalcon&
    # var-prome=falcon_group_data_system_openfalcon&
    # &var-group_name_point=data.system.openfalcon
    :return:
    '''
    prome_metric = replace_str_for_counter(metric_p.split('/',1)[0])

    grp_l = replace_str_for_counter(grp_p)
    metric_l = replace_str_for_counter(metric_p)
    url = '{}&var-grp_name={}&var-group_name_point={}&var-falcon_poly_name=falcon_group_poly_{}&var-prome=falcon_group_{}&var-poly_res_sum=poly_res_{}_sum&var-poly_res_avg=poly_res_{}_avg&var-metric_line={}&var-metric={}&var-prome_metric={}'.format(

        GRAFANA_SINGLE_POLY_URL,grp_l, grp_p, grp_l, grp_l, prome_metric, prome_metric, metric_l, metric_p,prome_metric)
    # print(url)
    return url


@app.route('/portal/poly')
def polys_get():
    page = int(request.args.get('p', 1))
    limit = int(request.args.get('limit', 20))
    query = request.args.get('q', '').strip()
    mine = request.args.get('mine', '1')
    me = g.user.name if mine == '1' else None
    vs, total = PolyMetric.query(page, limit, query, me)

    new_vs = []
    for v in vs:
        setattr(v,'g_url',gen_single_poly_grafana_link(v.name,v.counter))
        new_vs.append(v)
    return render_template(
        'portal/poly/list.html',
        data={
            # 'vs': vs,
            'vs': new_vs,
            'total': total,
            'query': query,
            'limit': limit,
            'page': page,
            'mine': mine,
        }
    )


@app.route('/portal/poly/add')
def poly_update_get():
    o = PolyMetric.get(int(request.args.get('poly_id', '0').strip()))
    return render_template('portal/poly/add.html', data={'poly': o})


@app.route('/portal/poly/update', methods=['POST'])
def poly_update_post():
    poly_id = request.form['poly_id'].strip()
    name = request.form['name'].strip()
    poly_type = request.form['poly_type'].strip()
    counter = request.form['counter'].strip()
    msg = required_chk({
        'name': name,
        'poly_type': poly_type,
        'counter': counter,
    })

    if msg:
        return jsonify(msg=msg)
    name = name.split("\n")
    counter = counter.split("\n")
    if len(name) == 0 or len(counter) == 0:
        return jsonify(msg="name empty or counter empty")
    res = dict()
    for n in name:
        if not n:
            continue

        for c in counter:
            if not c:
                continue
            rr = PolyMetric.save_or_update(
                poly_id,
                n,
                poly_type,
                c,
                g.user.name,
            )
            if rr:
                res["name_{}_counter_{}".format(n, c)] = rr
    if not res:
        return jsonify(msg='')
    return jsonify(msg=str(res))
    # return jsonify(msg=PolyMetric.save_or_update(
    #     poly_id,
    #     name,
    #     poly_type,
    #     counter,
    #     g.user.name,
    # ))


@app.route('/portal/poly/delete/<poly_id>')
def poly_delete_get(poly_id):
    poly_id = int(poly_id)
    PolyMetric.delete_one(poly_id)
    return jsonify(msg='')
