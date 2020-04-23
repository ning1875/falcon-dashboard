#!/bin/bash

WORKSPACE=$(cd $(dirname $0)/; pwd)
cd $WORKSPACE

mkdir -p var

gun=/data00/pyenv/versions/2.7.14/bin/gunicorn


module=dashboard
app=falcon-$module
pidfile=var/app.pid
logfile=var/app.log

function get_config(){
	#china
	#server 10.14.68.137:8082 max_fails=50 weight=3;
	#server 10.14.68.138:8082 max_fails=50 weight=3;
	#server 10.14.68.139:8082 max_fails=50 weight=3;

	#maliva
	#server 10.110.8.53:8081 max_fails=50 weight=3;
	#server 10.110.11.10:8082 max_fails=50 weight=3;

	BASE_DIR=`pwd`
	RRD_DIR="${BASE_DIR}/rrd"

	local_ip=`hostname -i`
	if [ -z ${local_ip} ];then
		echo "Cannot get local ip and cannot get config.py, exit"
		exit 1
	fi

	b_ip=`echo ${local_ip}|cut -d. -f2`
	mv ${RRD_DIR}/config.py ${RRD_DIR}/config.py.`date +"%F-%T"|tr ":" "-"`
	if [ ${b_ip} -gt 108 ];then
		region="maliva"
	else
		region="china"
	fi

	/bin/cp -rf ${RRD_DIR}/config/config_${region}.py ${RRD_DIR}/config.py
	if [ $? -ne 0 ];then
		echo "Cp config fail, exit"
		exit 1
	fi
	
	echo "start ${region}..."
}

function check_pid() {
    if [ -f $pidfile ];then
        pid=`cat $pidfile`
        if [ -n $pid ]; then
            running=`ps -p $pid|grep -v "PID TTY" |wc -l`
            return $running
        fi
    fi
    return 0
}

function start() {
    source env/bin/activate

    #prepare config file
    get_config

    hash ${gun} 2>&- || { echo >&2 "I require gunicorn but it's not installed.  Aborting."; exit 1; }

    ##check_pid
    #running=$?
    #if [ $running -gt 0 ];then
    #    echo -n "$app now is running already, pid="
    #    cat $pidfile
    #    return 1
    #fi

#    gunicorn -c gunicorn.conf wsgi:app -D -t 6000 --pid $pidfile --access-logfile $logfile --error-logfile $logfile --log-level debug
    ${gun} -c gunicorn.conf wsgi:app -D -t 6000 --pid $pidfile
    sleep 1
    echo -n "$app started..., pid="
    cat $pidfile
}

function stop() {
    ps -ef |grep gunicorn.conf |grep 6000 |grep -v grep |awk '{print $2}' |xargs kill

    echo "$app quit..."
}

function kill9() {
    pid=`cat $pidfile`
    kill -9 $pid
    echo "$app stoped..."
}

function restart() {
    stop
    sleep 2
    start
}

function status() {
    check_pid
    running=$?
    if [ $running -gt 0 ];then
        echo -n "$app now is running, pid="
        cat $pidfile
    else
        echo "$app is stoped"
    fi
}

function tailf() {
    tail -f $logfile
}

function show_version() {
    cat gitversion
}

function pack() {
    git log -1 --pretty=%h > gitversion
    file_list="control  gunicorn.conf  pip_requirements.txt  README.md  rrd  wsgi.py"
    echo "...tar $app.tar.gz <= $file_list"
    gitversion=`cat gitversion`
    tar -zcf $app-$gitversion.tar.gz  gitversion $file_list
}

function help() {
    echo "$0 start|stop|restart|status|tail|kill9|version|pack"
}

if [ "$1" == "" ]; then
    help
elif [ "$1" == "stop" ];then
    stop
elif [ "$1" == "kill9" ];then
    kill9
elif [ "$1" == "start" ];then
    start
elif [ "$1" == "restart" ];then
    restart
elif [ "$1" == "status" ];then
    status
elif [ "$1" == "tail" ];then
    tailf
elif [ "$1" == "pack" ];then
    pack
elif [ "$1" == "version" ];then
    show_version
else
    help
fi
