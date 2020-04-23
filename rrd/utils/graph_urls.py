#-*- coding:utf-8 -*-
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
import copy
import re
from rrd import config
from rrd.model.tmpgraph import TmpGraph
from rrd.model.endpoint import Endpoint, EndpointCounter
from rrd.config import today_date_str

def generate_graph_urls(graph, start, end):
    print today_date_str(),"generate_graph_urls_start",graph.counters
    counters = graph.counters or []
    if not counters:
        return []

    endpoint_list = graph.hosts or []
    if not endpoint_list:
        return []

    endpoint_objs = Endpoint.gets_by_endpoint(endpoint_list)
    print today_date_str(),"generate_graph_urls_endpoint_objs"
    if not endpoint_objs:
        return []
    endpoint_ids = [x.id for x in endpoint_objs]

    counters = []
    print today_date_str(), len(graph.counters)
    for c in graph.counters:
        print today_date_str(),"c",c
        if c.find("metric=") == -1:
            counters.append(c)
        else:
            metric=""
            tags = []
            qs = []
            c = c.strip()
            for q in c.split():
                q = q.strip()
                if q.startswith("metric="):
                    metric = q.replace("metric=", "^", 1)
                    qs.append(metric)
                else:
                    qs.append(q)
                    tags.append(q)
            print "counter_objs_start"
            counter_objs = EndpointCounter.search_in_endpoint_ids(qs, endpoint_ids[:], limit=100)
            print "counter_objs",counter_objs

            if not counter_objs:
                continue
            for co in counter_objs:
                if not re.search('^%s(/|$)' %metric, co.counter):
                    continue

                matched = True
                for tag in tags:
                    if not re.search('(/|,)%s(,|$)' %tag, co.counter):
                        matched = False
                        break
                if not matched:
                    continue

                counters.append(co.counter)
    if not counters:
        return []
    counters = sorted(list(set(counters)))

    return _generate_graph_urls(graph, counters, endpoint_list, start, end)

def _generate_graph_urls(graph, counters, endpoint_list, start, end):
    print today_date_str(),"_generate_graph_urls_start"
    ret_graphs = []
    print today_date_str(),"graph.graph_type",graph.graph_type
    if graph.graph_type == 'h':
        for c in counters:
            print today_date_str(), "tmp_graph_id_start"
            tmp_graph_id = TmpGraph.add(endpoint_list, [c,])
            if not tmp_graph_id:
                break

            new_g = copy.deepcopy(graph)
            new_g.counters = c
            if end:
                new_g.src = '''/chart/h?id=%s&start=%s&end=%s''' %(tmp_graph_id, start or (0-graph.timespan), end)
            else:
                new_g.src = '''/chart/h?id=%s&start=%s''' %(tmp_graph_id, start or (0-graph.timespan))
            if graph.method == 'SUM':
                new_g.src += "&sum=on"
            else:
                new_g.src += "&cf=%s" %graph.method

            ret_graphs.append(new_g)
    elif graph.graph_type=='k':
        for e in endpoint_list:
            tmp_graph_id = TmpGraph.add([e,], counters)
            if not tmp_graph_id:
                break

            new_g = copy.deepcopy(graph)
            new_g.hosts = e
            if end:
                new_g.src = '''/chart/k?id=%s&start=%s&end=%s''' %(tmp_graph_id, start or (0-graph.timespan), end)
            else:
                new_g.src = '''/chart/k?id=%s&start=%s''' %(tmp_graph_id, start or (0-graph.timespan))
            if graph.method == 'SUM':
                new_g.src += "&sum=on"
            else:
                new_g.src += "&cf=%s" %graph.method

            ret_graphs.append(new_g)
    else:
        #组合视角
        tmp_graph_id = TmpGraph.add(endpoint_list, counters)
        if not tmp_graph_id:
            return []
        new_g = copy.deepcopy(graph)
        if end:
            new_g.src = '''/chart/a?id=%s&start=%s&end=%s''' %(tmp_graph_id, start or (0-graph.timespan), end)
        else:
            new_g.src = '''/chart/a?id=%s&start=%s''' %(tmp_graph_id, start or (0-graph.timespan))
        if graph.method == 'SUM':
            new_g.src += "&sum=on"
        else:
            new_g.src += "&cf=%s" %graph.method

        ret_graphs.append(new_g)

    return ret_graphs

