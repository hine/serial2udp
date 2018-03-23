import sys
import time
import threading
import socket

import serial


class Proxy(object):
    """
    """
    def __init__(self):
        self._is_started = False

        self._serial_send_port = None

        self._udp_send_ip = None
        self._udp_send_port = None

    def serial_connect(self, port:str, baudrate:int=115200, timeout=0):
        # シリアル接続のポートを開く
        self._serial = serial.Serial(port=port, baudrate=baudrate)

        # 受信スレッドを立ち上げ
        self._serial_receiver_thread = threading.Thread(target=self._serial_receiver)
        self._serial_receiver_thread.setDaemon(True)
        self._serial_receiver_thread.start()

    def _serial_receiver(self):
        while True:
            data = self._serial.read(size=1)
            self._udp_send(data)

    def _serial_send(self, message):
        if self._is_started:
            self._serial.write(message)

    def udp_connect(self, listen_ip:str, listen_port:int, send_ip:str, send_port:int):
        # UDP送信先の登録
        self._udp_send_ip = send_ip
        self._udp_send_port = send_port

        # UDP送受信用Socket生成
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((listen_ip, listen_port))

        # 受信スレッドを立ち上げ
        self._udp_receiver_thread = threading.Thread(target=self._udp_receiver)
        self._udp_receiver_thread.setDaemon(True)
        self._udp_receiver_thread.start()

    def _udp_receiver(self):
        while True:
            message, udp_response_ip, udp_response_port = self._sock.recvfrom(1)
            self._serial_send(message)
            # 送信元情報でレスポンス先を訂正
            self._udp_send_ip = udp_response_ip
            self._udp_send_port = udp_response_port
    
    def _udp_send(self, message):
        if self._is_started:
            self._sock.sendto(message, (self._udp_send_ip, self._udp_send_port))

    def start_proxy(self):
        self._is_started = True

def main():
    args = sys.argv
    serial_port = args[1]
    serial_baudrate = int(args[2])
    udp_listen_ip = args[3]
    udp_listen_port = int(args[4])
    udp_send_ip = args[5]
    udp_send_port = int(args[6])

    s2u = Proxy()
    s2u.serial_connect(serial_port, serial_baudrate)
    s2u.udp_connect(udp_listen_ip, udp_listen_port, udp_send_ip, udp_send_port)
    s2u.start_proxy()

    while True:
        time.sleep(1)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
