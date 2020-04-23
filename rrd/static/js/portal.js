// - business function -
function query_user() {
    var query = $.trim($("#query").val());
    var mine = document.getElementById('mine').checked ? 1 : 0;
    var amstag = document.getElementById('amstag').checked ? 1 : 0;
    window.location.href = '/portal/hostgroup?q=' + query + '&mine=' + mine + '&amstag=' + amstag;
}

function query_user_amstag() {
    var query = $.trim($("#query").val());
    var mine = document.getElementById('mine').checked ? 1 : 0;
    var amstag = document.getElementById('amstag').checked ? 1 : 0;
    window.location.href = '/portal/hostgrouptag?q=' + query + ' &mine=' + mine + '&amstag=' + amstag;
}

function create_hostgroup() {
    var name = $.trim($("#grp_name").val());
    $.post('/portal/group/create', {'grp_name': name}, function (json) {
        handle_quietly(json, function () {
            window.location.reload();
        });
    }, "json");
}

function delete_hostgroup(group_id) {
    my_confirm('确定要删除？？？', ['确定', '取消'], function () {
        $.getJSON('/portal/group/delete/' + group_id, {}, function (json) {
            handle_quietly(json, function () {
                location.reload();
            });
        });
    }, function () {
        return false;
    });
}

function edit_hostgroup(group_id, grp_name) {
    layer.prompt({title: 'input new name:', val: grp_name, length: 255}, function (val, index, elem) {
        $.post('/portal/group/update/' + group_id, {'new_name': val}, function (json) {
            handle_quietly(json, function () {
                location.reload();
            });
        }, "json");
    })
}

function rename_hostgroup() {
    var old_str = $.trim($('#old_str').val());
    var new_str = $.trim($('#new_str').val());
    $.post('/portal/group/rename', {'old_str': old_str, 'new_str': new_str}, function (json) {
        handle_quietly(json, function () {
            window.location.href = '/?q=' + new_str;
        });
    }, "json");
}

function bind_plugin(group_id) {
    var plugin_idr = $.trim($("#plugin_dir").val());
    $.post('/portal/plugin/bind', {'group_id': group_id, 'plugin_dir': plugin_idr}, function (json) {
        handle_quietly(json, function () {
            location.reload();
        });
    }, "json");
}

function unbind_plugin(plugin_id) {
    my_confirm('确定要解除绑定？', ['确定', '取消'], function () {
        $.getJSON('/portal/plugin/delete/' + plugin_id, {}, function (json) {
            handle_quietly(json, function () {
                location.reload();
            });
        });
    }, function () {
        return false;
    });
}

function query_host() {
    var xbox = $("#xbox").val();
    var group_id = $("#group_id").val();
    var query = $.trim($("#query").val());
    var limit = $("#limit").val();
    var maintaining = document.getElementById('maintaining').checked ? 1 : 0;
    window.location.href = '/portal/group/' + group_id + '/hosts?q=' + query + '&maintaining=' + maintaining + '&limit=' + limit + '&xbox=' + xbox;
}

function select_all() {
    var v = document.getElementById('chk').checked;
    $.each($("#hosts input[type=checkbox]"), function (i, n) {
        n.checked = v;
    });
}

function remove_hosts() {
    var ids = [];
    jQuery.each($("#hosts input[type=checkbox]"), function (i, n) {
        if (n.checked) {
            ids.push($(n).attr("hid"));
        }
    });
    if (ids.length == 0) {
        err_message_quietly('no hosts selected');
        return;
    }

    var group_id = $("#group_id").val();
    $.post("/portal/host/remove", {'host_ids': ids.join(","), 'grp_id': group_id}, function (json) {
        handle_quietly(json, function () {
            location.reload();
        });
    }, "json");
}

function maintain() {
    var ids = [];
    jQuery.each($("#hosts input[type=checkbox]"), function (i, n) {
        if (n.checked) {
            ids.push($(n).attr("hid"));
        }
    });
    if (ids.length == 0) {
        err_message_quietly('no hosts selected');
        return;
    }

    var begin = $.trim($("#begin").val());
    var end = $.trim($("#end").val());

    if (begin.length == 0 || end.length == 0) {
        err_message_quietly('begin time and end time are necessary');
        return false;
    }

    var b = moment(begin, "YYYY-MM-DD HH:mm").unix();
    var e = moment(end, "YYYY-MM-DD HH:mm").unix();

    $.post('/portal/host/maintain', {'begin': b, 'end': e, 'host_ids': ids.join(',')}, function (json) {
        handle_quietly(json, function () {
            location.reload();
        });
    }, "json");
}

function no_maintain() {
    var ids = [];
    jQuery.each($("#hosts input[type=checkbox]"), function (i, n) {
        if (n.checked) {
            ids.push($(n).attr("hid"));
        }
    });
    if (ids.length == 0) {
        err_message_quietly('no hosts selected');
        return;
    }

    $.post('/portal/host/reset', {'host_ids': ids.join(',')}, function (json) {
        handle_quietly(json, function () {
            location.reload();
        });
    }, "json");
}

function batch_add_host() {
    var hosts = $.trim($("#hosts").val());
    if (hosts.length == 0) {
        err_message_quietly('请填写机器列表，一行一个');
        return false;
    }

    $.post('/portal/host/add', {'group_id': $("#group_id").val(), 'hosts': hosts}, function (json) {
        if (json.msg.length > 0) {
            err_message_quietly(json.msg);
        } else {
            $("#message").html(json.data);
        }
    }, "json");
}

function host_unbind_group(host_id, group_id) {
    $.getJSON('/portal/host/unbind', {'host_id': host_id, 'group_id': group_id}, function (json) {
        handle_quietly(json, function () {
            location.reload();
        });
    })
}

function query_alarm() {
    var query = $.trim($("#query").val());
    if (query == "") {
        $("#alarm").html('<div class="alert alert-danger alert-dismissable" > ' +
            '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>' +
            ' 没有验证成功的实例. </div>');
        return false;
    }
    window.location.href = '/portal/alarm?q=' + query;
}


function query_expression() {
    var query = $.trim($("#query").val());
    var mine = document.getElementById('mine').checked ? 1 : 0;
    window.location.href = '/portal/expression?q=' + query + '&mine=' + mine;
}

function delete_expression(id) {
    my_confirm('确定要删除？？？', ['确定', '取消'], function () {
        $.getJSON('/portal/expression/delete/' + id, {}, function (json) {
            handle_quietly(json, function () {
                location.reload();
            });
        })
    }, function () {
        return false;
    });
}

function update_expression() {
    var callback_url = $.trim($("#callback_url").val());
    var need_callback = callback_url.length > 0 ? 1 : 0;
    $.post(
        '/portal/expression/update',
        {
            'expression': $.trim($("#expression").val()),
            'func': $.trim($("#func").val()),
            'op': $("#op").val(),
            'right_value': $.trim($("#right_value").val()),
            'uic': $.trim($("#uic").val()),
            'max_step': $.trim($("#max_step").val()),
            'priority': $.trim($("#priority").val()),
            'note': $.trim($("#note").val()),
            'url': callback_url,
            'callback': need_callback,
            'before_callback_sms': document.getElementById("before_callback_sms").checked ? 1 : 0,
            'before_callback_mail': document.getElementById("before_callback_mail").checked ? 1 : 0,
            'after_callback_sms': document.getElementById("after_callback_sms").checked ? 1 : 0,
            'after_callback_mail': document.getElementById("after_callback_mail").checked ? 1 : 0,
            'expression_id': $("#expression_id").val()
        },
        function (json) {
            handle_quietly(json);
        }, "json");
}

function pause_expression(id) {
    var pause = '1';
    if ($('#i-' + id).attr('class').indexOf('play') > 0) {
        // current: pause
        pause = '0'
    }
    $.getJSON("/portal/expression/pause", {'id': id, 'pause': pause}, function (json) {
        if (json.msg.length > 0) {
            err_message_quietly(json.msg);
        } else {
            if (pause == '1') {
                $('#i-' + id).attr('class', 'glyphicon glyphicon-play orange')
            } else {
                $('#i-' + id).attr('class', 'glyphicon glyphicon-pause orange')
            }
        }
    });
}

function make_select2_for_uic_group(selector) {
    $(selector).select2({
        placeholder: "input uic team name",
        allowClear: true,
        multiple: true,
        quietMillis: 100,
        minimumInputLength: 2,
        id: function (obj) {
            return obj.name;
        },
        ajax: {
            url: "/api/uic/group",
            dataType: 'json',
            data: function (term, page) {
                return {
                    query: term,
                    limit: 2000
                };
            },
            results: function (json, page) {
                return {results: json.data};
            }
        },

        initSelection: function (element, callback) {
            var data = [];
            $($(element).val().split(",")).each(function () {
                data.push({id: this, name: this});
            });
            callback(data);
        },

        formatResult: function (obj) {
            return obj.name
        },
        formatSelection: function (obj) {
            return obj.name
        }
    });
}

function query_template() {
    var query = $.trim($("#query").val());
    var mine = document.getElementById('mine').checked ? 1 : 0;
    window.location.href = '/portal/template?q=' + query + '&mine=' + mine;
}


function delete_template(id) {
    my_confirm('确定要删除？？？', ['确定', '取消'], function () {
        $.getJSON('/portal/template/delete/' + id, {}, function (json) {
            handle_quietly(json, function () {
                location.reload();
            });
        })
    }, function () {
        return false;
    });
}

function query_poly() {
    var query = $.trim($("#query").val());
    var mine = document.getElementById('mine').checked ? 1 : 0;
    window.location.href = '/portal/poly?q=' + query + '&mine=' + mine;
}

function delete_service(id) {
    my_confirm('确定要删除？？？', ['确定', '取消'], function () {
        $.getJSON('/portal/service/delete/' + id, {}, function (json) {
            handle_quietly(json, function () {
                location.reload();
            });
        })
    }, function () {
        return false;
    });
}

function query_service() {
    var query = $.trim($("#query").val());
    var mine = document.getElementById('mine').checked ? 1 : 0;
    window.location.href = '/portal/service?q=' + query + '&mine=' + mine;
}

function delete_poly(id) {
    my_confirm('确定要删除？？？', ['确定', '取消'], function () {
        $.getJSON('/portal/poly/delete/' + id, {}, function (json) {
            handle_quietly(json, function () {
                location.reload();
            });
        })
    }, function () {
        return false;
    });
}

function create_template() {
    var tpl_name = $.trim($("#tpl_name").val());
    $.post('/portal/template/create', {'name': tpl_name}, function (json) {
        if (json.msg.length > 0) {
            err_message_quietly(json.msg);
        } else {
            location.href = '/portal/template/update/' + json.id;
        }
    }, "json");
}

function make_select2_for_template(selector) {
    $(selector).select2({
        placeholder: "input template name",
        allowClear: true,
        quietMillis: 100,
        minimumInputLength: 2,
        id: function (obj) {
            return obj.id;
        },
        ajax: {
            url: "/api/template/query",
            dataType: 'json',
            data: function (term, page) {
                return {
                    query: term,
                    limit: 10
                };
            },
            results: function (json, page) {
                return {results: json.data};
            }
        },

        initSelection: function (element, callback) {
            var tpl_id = $(element).val();
            $.getJSON("/api/template/" + tpl_id, function (json) {
                callback(json.data);
            });
        },

        formatResult: function (obj) {
            return obj.name
        },
        formatSelection: function (obj) {
            return obj.name
        }
    });
}

function make_select2_for_metric(selector) {
    $(selector).select2({
        placeholder: "input metric",
        allowClear: true,
        quietMillis: 100,
        minimumInputLength: 2,
        id: function (obj) {
            return obj.name;
        },
        ajax: {
            url: "/api/metric/query",
            dataType: 'json',
            data: function (term, page) {
                return {
                    query: term,
                    limit: 10
                };
            },
            results: function (json, page) {
                return {results: json.data};
            }
        },

        initSelection: function (element, callback) {
            var val = $(element).val();
            callback({id: val, name: val});
        },

        formatResult: function (obj) {
            return obj.name
        },
        formatSelection: function (obj) {
            return obj.name
        }
    });
}

function update_template() {
    var tpl_id = $('#tpl_id').val();
    var name = $.trim($("#name").val());
    var parent_id = $("#parent_id").val();
    $.post('/portal/template/rename/' + tpl_id, {'name': name, 'parent_id': parent_id}, function (json) {
        handle_quietly(json);
    }, "json");
}

function save_action_for_tpl(tpl_id) {
    var callback_url = $.trim($("#callback_url").val());
    var need_callback = callback_url.length > 0 ? 1 : 0;
    var lark_group_id = $.trim($("#lark_group_id").val());

    $.post(
        '/portal/template/action/update/' + tpl_id,
        {
            'uic': $.trim($("#uic").val()),
            'lark_group_id': lark_group_id,
            'url': callback_url,
            'callback': need_callback,
            'before_callback_sms': document.getElementById("before_callback_sms").checked ? 1 : 0,
            'before_callback_mail': document.getElementById("before_callback_mail").checked ? 1 : 0,
            'after_callback_sms': document.getElementById("after_callback_sms").checked ? 1 : 0,
            'after_callback_mail': document.getElementById("after_callback_mail").checked ? 1 : 0
        },
        function (json) {
            handle_quietly(json);
        }, "json");
}

function goto_strategy_add_div() {
    $("#add_div").show('fast');
    $("#current_sid").val('');
    location.href = "#add";
}

// function save_strategy() {
//     var sid = $("#current_sid").val();
//     $.post('/portal/strategy/update', {
//         'sid': sid,
//         'metric': $.trim($("#metric").val()),
//         'tags': $.trim($("#tags").val()),
//         'max_step': $.trim($("#max_step").val()),
//         'priority': $.trim($("#priority").val()),
//         'note': $.trim($("#note").val()),
//         'func': $.trim($("#func").val()),
//         'op': $.trim($("#op").val()),
//         'right_value': $.trim($("#right_value").val()),
//         'run_begin': $.trim($("#run_begin").val()),
//         'run_end': $.trim($("#run_end").val()),
//         'tpl_id': $.trim($("#tpl_id").val())
//     }, function (json) {
//         handle_quietly(json, function () {
//             location.reload();
//         });
//     }, "json")
// }

function save_strategy() {


    var sid = GetArray($("[data-sid]"));
    var metric = GetArray($("[data-metric]"));
    var tags = GetArray($("[data-tags]"));
    var func = GetArray($("[data-func]"));
    var op = GetArray($("[data-op]"));
    var right_value = GetArray($("[data-right_value]"));
    // console.log(sid, metric, tags, func, op, right_value)
    $.ajax({
        type: "post",
        url: '/portal/strategy/update',
        async: false, // 使用同步方式
        // 1 需要使用JSON.stringify 否则格式为 a=2&b=3&now=14...
        // 2 需要强制类型转换，否则格式为 {"a":"2","b":"3"}
        data: JSON.stringify({
            'sid': sid,
            'metric': metric,
            'tags': tags,
            'max_step': $.trim($("#max_step").val()),
            'priority': $.trim($("#priority").val()),
            'note': $.trim($("#note").val()),
            'func': func,
            'op': op,
            'right_value': right_value,
            'run_begin': $.trim($("#run_begin").val()),
            'run_end': $.trim($("#run_end").val()),
            'tpl_id': $.trim($("#tpl_id").val()),
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            handle_quietly(data, function () {
                location.reload();
            })
        } // 注意不要在此行增加逗号
    });


}

function GetArray(obj) {
    var arr = new Array()
    obj.each(function () {
        arr.push($(this).val())
    })
    return arr
}

function clone_strategy(sid) {
    $("#current_sid").val('');
    fill_fields(sid, false);
}

function modify_strategy(sid) {
    $("#current_sid").val(sid);
    fill_fields(sid, true);
}

function fill_fields(sid, is_modify) {
    //
    $("#add_div").show('fast');
    location.href = "#add";
    $.getJSON('/portal/strategy/' + sid, {}, function (json) {
        // 先判断是否要+元素
        //  先删除所有添加的metirc行
        $("[data-delete]").each(function () {
            deleteStrategy(this)
            // $(this).val(json.data[index].sid)
        });
        var len = json.data.length;
        if (len > 1) {
            for (var i = 0; i < len - 1; i++) {
                addStrategy()
            }

        }

        // 填充数据
        //   公共数据
        var first_one = json.data[0];
        $("#max_step").val(first_one.max_step);
        $("#priority").val(first_one.priority);
        $("#note").val(first_one.note);
        $("#run_begin").val(first_one.run_begin);
        $("#run_end").val(first_one.run_end);

        var sid = $("[data-sid]")
        var metric = $("[data-metric]")
        var tags = $("[data-tags]")
        var func = $("[data-func]")
        var op = $("[data-op]")
        var right_value = $("[data-right_value]")

        if (is_modify) {
            sid.each(function (index) {
                $(this).val(json.data[index].id)
            });
        }


        metric.each(function (index) {
            $(this).val(json.data[index].metric)
        });
        tags.each(function (index) {
            $(this).val(json.data[index].tags)
        });
        func.each(function (index) {
            $(this).val(json.data[index].func)
        });
        op.each(function (index) {
            $(this).val(json.data[index].op)
        });
        right_value.each(function (index) {
            $(this).val(json.data[index].right_value)
        });

        make_select2_for_metric("#metric");
    });
}

function delete_strategy(id) {
    my_confirm('确定要删除？？？', ['确定', '取消'], function () {
        $.getJSON('/portal/strategy/delete/' + id, {}, function (json) {
            handle_quietly(json, function () {
                location.reload();
            });
        })
    }, function () {
        return false;
    });
}

function tpl_unbind_group(tpl_id, grp_id) {
    my_confirm('确定要解除绑定关系？', ['确定', '取消'], function () {
        $.getJSON('/portal/template/unbind/group', {'tpl_id': tpl_id, 'grp_id': grp_id}, function (json) {
            handle_quietly(json, function () {
                location.reload();
            });
        })
    }, function () {
        return false;
    });
}

function fork_template(tpl_id) {
    $.getJSON('/portal/template/fork/' + tpl_id, {}, function (json) {
        if (json.msg.length > 0) {
            err_message_quietly(json.msg);
        } else {
            location.href = '/portal/template/update/' + json.id;
        }
    });
}

function bind_template(grp_id) {
    var tpl_id = $.trim($("#tpl_id").val());
    $.getJSON('/portal/group/bind/template', {'grp_id': grp_id, 'tpl_id': tpl_id}, function (json) {
        handle_quietly(json, function () {
            location.reload();
        })
    });
}

function node_unbind_tpl(grp_name, tpl_id) {
    my_confirm('确定要解除绑定关系？', ['确定', '取消'], function () {
        $.getJSON('/portal/template/unbind/node', {'tpl_id': tpl_id, 'grp_name': grp_name}, function (json) {
            handle_quietly(json, function () {
                location.reload();
            });
        })
    }, function () {
        return false;
    });
}

function node_bind_tpl() {
    var node = $.trim($("#node").val());
    var tpl_id = $("#tpl_id").val();
    $.post('/portal/template/bind/node', {'node': node, 'tpl_id': tpl_id}, function (json) {
        handle_quietly(json, function () {
            location.reload();
        });
    }, "json");
}

function create_cluster_monitor_metric(grp_id) {
    $.post('/portal/group/' + grp_id + '/cluster/creator', {
        'numerator': $("#numerator").val(),
        'denominator': $("#denominator").val(),
        'endpoint': $("#endpoint").val(),
        'metric': $("#metric").val(),
        'tags': $("#tags").val(),
        'step': $("#step").val()
    }, function (json) {
        handle_quietly(json, function () {
            location.href = "/portal/group/" + grp_id + "/cluster";
        });
    }, "json")
}


function sync_tag() {
    var tags = $.trim($("#tag_names").val());

    var newtags = tags.split(/[(\r\n)\r\n]+/);
    var simple = $("#simple").val();
    var new_simple = false
    if (simple == "0") {
        new_simple = false
    } else {
        new_simple = true
    }
    console.log("tags", newtags);

    $.ajax({
        type: "post",
        url: '/api/synctag',
        async: false, // 使用同步方式
        // 1 需要使用JSON.stringify 否则格式为 a=2&b=3&now=14...
        // 2 需要强制类型转换，否则格式为 {"a":"2","b":"3"}
        data: JSON.stringify({
            'tag_names': newtags,
            'region': $("#region").val(),
            'simple': new_simple,
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (json) {
            // ok_message_quietly(json)
            ok_message_quietly("successfully:-)", function () {
            });
            // handle_quietly(json, function () {
            //     location.reload();
            // });
        } // 注意不要在此行增加逗号
    });


    // $.post('/api/synctag', {
    //     'tag_names': tags,
    //     'region': $("#region").val(),
    //     'simple': new_simple,
    // }, function (json) {
    //     handle_quietly(json);
    // }, "json");
}

function update_cluster_monitor_metric(cluster_id, grp_id) {
    $.post('/portal/cluster/edit/' + cluster_id, {
        'numerator': $("#numerator").val(),
        'denominator': $("#denominator").val(),
        'endpoint': $("#endpoint").val(),
        'metric': $("#metric").val(),
        'tags': $("#tags").val(),
        'step': $("#step").val(),
        'grp_id': grp_id
    }, function (json) {
        handle_quietly(json);
    }, "json");
}

function delete_cluster_monitor_item(cluster_id) {
    my_confirm('确定要删除？？？', ['确定', '取消'], function () {
        $.post('/portal/cluster/delete/' + cluster_id, {}, function (json) {
            handle_quietly(json, function () {
                location.reload();
            })
        }, "json");
    }, function () {
        return false;
    });
}

// - alarm-dash business function -
function alarm_case_all_select() {
    var boxes = $("input[type=checkbox]");
    for (var i = 0; i < boxes.length; i++) {
        boxes[i].checked = "checked";
    }
}

function alarm_case_event_all_select() {
    var boxes = $("input[type=checkbox]");
    for (var i = 0; i < boxes.length; i++) {
        boxes[i].checked = "checked";
    }
}

function alarm_case_reverse_select() {
    var boxes = $("input[type=checkbox]");
    for (var i = 0; i < boxes.length; i++) {
        if (boxes[i].checked) {
            boxes[i].checked = ""
        } else {
            boxes[i].checked = "checked";
        }
    }
}

function alarm_case_event_reverse_select() {
    var boxes = $("input[type=checkbox]");
    for (var i = 0; i < boxes.length; i++) {
        if (boxes[i].checked) {
            boxes[i].checked = ""
        } else {
            boxes[i].checked = "checked";
        }
    }
}

function alarm_case_batch_rm() {
    var boxes = $("input[type=checkbox]");
    var ids = []
    for (var i = 0; i < boxes.length; i++) {
        if (boxes[i].checked) {
            ids.push($(boxes[i]).attr("alarm"))
        }
    }

    my_confirm('确定要删除？？？', ['确定', '取消'], function () {
        $.post('/portal/alarm-dash/case/delete', {"ids": ids.join(',')}, function (json) {
            handle_quietly(json, function () {
                location.reload();
            });
        }, "json");
    }, function () {
        return false;
    });
}

function alarm_case_rm(id) {
    my_confirm('确定要删除？？？', ['确定', '取消'], function () {
        $.post('/portal/alarm-dash/case/delete', {"ids": id}, function (json) {
            handle_quietly(json, function () {
                location.reload();
            });
        }, "json");
    }, function () {
        return false;
    });
}

function alarm_case_event_rm(id) {
    my_confirm('确定要删除？？？', ['确定', '取消'], function () {
        $.post('/portal/alarm-dash/case/event/delete', {"ids": id}, function (json) {
            handle_quietly(json, function () {
                location.reload();
            });
        }, "json");
    }, function () {
        return false;
    });
}

function alarm_case_event_batch_rm() {
    var boxes = $("input[type=checkbox]");
    var ids = []
    for (var i = 0; i < boxes.length; i++) {
        if (boxes[i].checked) {
            ids.push($(boxes[i]).attr("alarm"))
        }
    }

    my_confirm('确定要删除？？？', ['确定', '取消'], function () {
        $.post('/portal/alarm-dash/case/event/delete', {"ids": ids.join(',')}, function (json) {
            handle_quietly(json, function () {
                location.reload();
            });
        }, "json");
    }, function () {
        return false;
    });
}


function addStrategy() {
    var fs = $("#first_strategy")

    fs.after("            <div class=\"form-inline mt10\" role=\"form\" >\n" +
        "                <div class=\"form-group\" >\n" +
        "                    metric:\n" +
        "                </div>\n" +
        " <input type=\"hidden\"  data-sid=\"sid\">\n" +
        "                <div class=\"form-group\">\n" +
        "                    <input type=\"text\" style=\"width: 300px;\" class=\"form-control\" id=\"metric\" data-metric='metric'>\n" +
        "                </div>\n" +
        "                tags: <input type=\"text\" class=\"form-control\" id=\"tags\" data-tags='tags'>\n" +
        "                <div class=\"form-group\">\n" +
        "                    if <input type=\"text\" value=\"all(#3)\" class=\"form-control\" id=\"func\" data-func='func' style=\"width: 100px;\">\n" +
        "                    <select class=\"form-control\" id=\"op\" data-op='op'>\n" +
        "                        <option value=\"==\">==</option>\n" +
        "                        <option value=\"!=\">!=</option>\n" +
        "                        <option value=\"<\">&lt;</option>\n" +
        "                        <option value=\"<=\">&lt;=</option>\n" +
        "                        <option value=\">\">&gt;</option>\n" +
        "                        <option value=\">=\">&gt;=</option>\n" +
        "                    </select>\n" +
        "                    <input type=\"text\" value=\"0\" class=\"form-control\" id=\"right_value\"  data-right_value='right_value' style=\"width: 100px;\">\n" +
        "                    : alarm(); callback();\n" +
        "                </div>\n" +
        "            <input type='button' class=\"btn btn-danger\" value='删除' data-delete='delete' onclick='deleteStrategy(this)'></div>")
}

function deleteStrategy(This) {
    //获取删除按钮的父元素 的 父元素 利用 爷爷元素 删除
    This.parentNode.parentNode.removeChild(This.parentNode);
}