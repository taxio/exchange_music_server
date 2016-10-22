#coding: utf-8
#!/usr/bin/python

import configparser
import socketserver
import sys

#UDPサーバー割り込み処理
class MyUDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip().decode('utf-8')
        user_list = data.split(",")
        device_user = user_list[0]
        passed_user = user_list[1:6]
        socket = self.request[1]
        print ("device user ID:{}".format(device_user))	#デバイスの持ち主のID
        print ("passed user ID:{}".format(passed_user))	#すれ違ったユーザーのID*5個


class DeviceServer:

    def __init__(self):
        self.inifile = configparser.SafeConfigParser()
        self.inifile.read('./device_server_config.ini')	#configファイルにてアドレスとポートを指定

    def run(self):
        #アドレスとポート設定
        HOST = self.inifile.get('settings','host')
        PORT = self.inifile.getint('settings','port')
        #サーバー立ち上げ
        server = socketserver.ThreadingUDPServer((HOST, PORT), MyUDPHandler)
        #割り込みループ
        server.serve_forever()

