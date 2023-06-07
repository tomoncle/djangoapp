# Create your tests here.

import json
import time

import paramiko
from django.shortcuts import render, HttpResponse

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


def ssh_cmd(cmd):
    ssh.connect("10.32.0.4", 22, "root", "123456")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read()
    if not result:
        result = stderr.read()
    ssh.close()
    return result.decode()


def test1(request):
    if request.method != "POST":
        return render(request, "webssh/test/test1.html")

    data = request.body.decode("utf-8")
    if data == "ok":
        a = ssh_cmd("ifconfig")
        return HttpResponse(a)


def test2(request):
    if request.method != "POST":
        return render(request, "webssh/test/test2.html")

    data = request.body.decode("utf-8")
    if data == "ok":
        a = ssh_cmd("apt")
        return HttpResponse(a)


def test3(request):
    if request.method != "POST":
        return render(request, "webssh/test/test3.html")

    data = request.body.decode("utf-8")
    json_data = json.loads(data)
    address = json_data.get("address")
    command = json_data.get("command")

    if not address or len(address) <= 1:
        return HttpResponse("主机地址或命令行不能为空...")

    if not command or len(command) <= 1:
        return HttpResponse("主机地址或命令行不能为空...")

    times = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    times = "---> \x1B[1;3;32m 执行时间: [ {} ] \x1B[0m".format(times)
    address = "\x1B[1;3;33m 主机地址: [ {} ] \x1B[0m".format(address)
    command = "\x1B[1;3;35m 执行命令: [ {} ] \x1B[0m".format(command)
    if ssh_cmd(command):
        value = times + address + command + "\x1B[1;3;25m 回执: [ok] \x1B[0m"
    else:
        value = times + address + command + "\x1B[1;3;20m 回执: [Error] \x1B[0m"
    return HttpResponse(value)


def test4(request):
    context = {'connect': {'host': '10.32.0.4', 'port': 22, 'user': 'root', 'password': '123456', 'host_name': "test"}}
    return render(request, "webssh/test/test4.html", context)
