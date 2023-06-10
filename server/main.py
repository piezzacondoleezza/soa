from format_parsers import *

import threading
import os
import socket
import struct

def parse_type():
    ser_time, deser_time, size = 0, 0, 0
    ser_type = os.getenv('SERIALIZATION_TYPE')
    match ser_type:
        case 'NATIVE':
            ser_time, deser_time, size = native_format()
        case 'JSON':
            ser_time, deser_time, size = json_format()
        case 'XML':
            ser_time, deser_time, size = xml_format()
        case 'GOOGLE_PROTOBUF':
            ser_time, deser_time, size = proto_format()
        case 'APACHE':
            ser_time, deser_time, size = avro_format()
        case 'YAML':
            ser_time, deser_time, size = yaml_format()
        case 'MESSAGEPACK':
            ser_time, deser_time, size = msg_pack_format()
    result = f'{ser_type}-{size}-{ser_time}ms-{deser_time}ms'
    return result

class MultiCastSocket():
    def __init__(self):
        self.multicast_group = os.getenv('MULTICAST_ADRESS')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.initialize()

    def initialize(self):
        proxy_address = ('', int(os.getenv('MULTICAST_PORT')))
        self.socket.bind(proxy_address)
        group = socket.inet_aton(self.multicast_group)
        self_ = socket.inet_aton('0.0.0.0')
        # mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, group + self_)

    def receive_respond_loop(self):
        while True:
            _, address = self.socket.recvfrom(1024)
            data = parse_type()
            self.socket.sendto(bytes(data + "\n", "utf-8"), address)

class UDPSocket():
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host, port = os.getenv('SERIALIZATION_TYPE'), int(os.getenv('PORT'))
        self.listening_address = (host, port)
        self.socket.bind(self.listening_address)

    def receive_respond_loop(self):
        while(True):
            _, address = self.socket.recvfrom(1024)
            data = parse_type()
            self.socket.sendto(bytes(data + "\n", "utf-8"), address)

if __name__ == "__main__":
    launchme = UDPSocket()
    launchme2 = MultiCastSocket()
    t1 = threading.Thread(target=launchme.receive_respond_loop)
    t2 = threading.Thread(target=launchme2.receive_respond_loop)
    for t in [t1, t2]: t.start()
    for t in [t1, t2]: t.join()
