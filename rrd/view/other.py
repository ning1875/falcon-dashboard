# -*- coding:utf-8 -*-

import json
import re
from flask import request, abort, g, render_template, jsonify
from rrd import app, config
from rrd import corelib
from rrd.config import redis_conn
import requests
import redis
from rrd.utils.grafana_bfc import bfc
from rrd.utils.lark_work import text_chat
from rrd.utils.format import now_date_str
from rrd import corelib
from concurrent.futures import ThreadPoolExecutor


def batch_call_alarm_api(data, type):
    for addr in config.ALARM_ADDRS:
        url = "http://{}:9912/blockmonitor".format(addr)
        if type == 'block':
            method = "POST"
        else:
            method = "DELETE"

        print(method,url)
        r = corelib.auth_requests_retry(
            method, url, data=data, headers={"Content-type": "application/json", }
        )
        # print(r.status_code, r.text)


@app.route('/monitor/block', methods=['POST'])
def create_block():
    # data = request.get_data()
    # req_data = json.loads(data)
    r = request.data
    req_data = json.loads(r)
    if req_data.get("type") == 'url_verification':
        return jsonify(req_data)
    block_info = req_data.get("action").get("value")
    user_name = block_info.get("user_name")
    counter = block_info.get("counter")
    time = block_info.get("time")
    type = block_info.get("type")
    print(user_name, counter, time, type)

    executor = ThreadPoolExecutor(1)
    executor.submit(batch_call_alarm_api, json.dumps(block_info), type)
    text = ''
    if type == 'block':

        text = '[ACK通知]\r\n{} 已ACK报警规则: Counter:{}   {} 分钟\r\n本消息发送时间:{}'.format(
            user_name,
            counter,
            time,
            now_date_str()
        )
    elif type == 'unblock':
        text = '[ACK通知]\r\n{} 已解除屏蔽报警规则: Counter:{}   \r\n本消息发送时间:{}'.format(
            user_name,
            counter,
            now_date_str()
        )

    text_chat(user_name, text)
    return jsonify(req_data)


@app.route('/portal/grafana/api/v1/monitors')
def grafana_bfc():
    res = bfc()
    return jsonify(res)
