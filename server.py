from aiohttp import web
import netmiko
import socketio
import requests
from netmiko import ConnectHandler
from getpass import getpass
import os
PORT = int(os.environ.get("PORT", 5000))

sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

connections = {}

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def privateCommand(sid,data):
    print("privateCommand ", data)
    print("dev ", data['devices'])
    output = ""
    print("command ", data)
    print("conn",connections[data['devices']])
    try:
        output = connections[data['devices']].send_config_set(data['command'], enter_config_mode=False, exit_config_mode=False, error_pattern=r'% Invalid input detected at')
        if output == "":
            output = 'Invalid command'
    except netmiko.exceptions.ConfigInvalidException as e:
        output = f"\n{str(e)}\n"

    await sio.emit('output'+data['devices'],output, room=sid)

    print("outtt:", output, "data: ", data['devices'])
    output = ""


@sio.event
async def command(sid, data):
    print("command ", data)
    print("message ", data['command'])
    output = ""
    print("command ", data['deviceId'])

    try:
        output = connections[data['deviceId']].send_config_set(data['command'],cmd_verify=True, enter_config_mode=False, exit_config_mode=False, error_pattern=r'% Invalid input detected at')

    except netmiko.exceptions.ConfigInvalidException as e:
        output = f"\n{str(e)}\n"

    await sio.emit('output'+data['deviceId'],output, room=sid)

    print("outtt:", output, "data: ", data['deviceId'])
    output = ""



@sio.event
async def createSSH(sid, data):
    print("DATA: ", data[0])
    devList = []
    for i,device in enumerate(data):
        print("DEV ", device, "i ", i)
        req = requests.get('http://localhost:5001/devices/selected/'+device)
        req = req.json()
        req[0].pop('_id')
        req[0].pop('name')
        req[0].pop('__v')
        devList.append(req)
        print("DEVLIST: ", devList)
        net_connect = ConnectHandler(**devList[i][0], timeout=10)
        net_connect.enable()
        connections[data[i]] = net_connect

    print("DEVLIST: ", devList)
    print("createSSH ", connections)


@sio.event
def disconnectSSH(sid, data):
    print("disconnectSSH ", data)
    connections[data].disconnect()
    connections.pop(data, None)
    print("disconnectSSH ", connections)



@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    web.run_app(app, port=PORT)


    # net_connect = ConnectHandler(**device[0], timeout=10)
    # net_connect.enable()

    # output= net_connect.send_config_set('do sh run')

    # print("Connected to device successful"+"\n"+net_connect.find_prompt())
    # print(output)


    # connections[data[0][0]] = net_connect
    # print("createSSH ", connections[data[0][0]])
    # out2=connections[data[0][0]].send_command('sh run')

  # response = connections[data['deviceId'][0][0]].send_command(data['command'])asd
    # connections[data['deviceId'][0][0]].enable()
    # print("response: ", response)
    # output= connections[data['deviceId'][0][0]].send_config_set(data['command'])

    # print("Connected to device successful"+"\n"+connections[data['deviceId'][0][0]].find_prompt())
    # await sio.emit('output'+data['deviceId'][0][0],output, room=sid)
