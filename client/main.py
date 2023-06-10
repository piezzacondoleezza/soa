import socketserver
import json
import os
import socket
import struct

class MyUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):

        data = self.request[0].strip()
        socket_receive = self.request[1]
        print("{} wrote:".format(self.client_address[0]))

        mapping = {}
        with open("conf.txt") as file:
            for line in file:
                (key, value) = line.split()
                mapping[key] = int(value)

        data_dict = json.loads(data.decode())

        if data_dict['type'] == 'get_result':
            ser_format = data_dict['format']
            port = mapping[ser_format]
            host = ser_format

            socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_send.sendto(bytes("", "utf-8"), (host, port))
            received = socket_send.recv(1024)

            socket_receive.sendto(received, self.client_address)
            socket_send.close()
        else:
            multicast_group = (os.getenv('MULTICAST_ADRESS'), int(os.getenv('MULTICAST_PORT')))
            sock_mult = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock_mult.settimeout(1)
            ttl = struct.pack('b', 1)
            sock_mult.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

            res = []

            sent = sock_mult.sendto(bytes(''+ "\n", "utf-8"), multicast_group)
            while len(res) < 7:
                data, server = sock_mult.recvfrom(1024)
                res.append(data)
            for answer in res:
                decoded_answer = answer.decode()
                socket_receive.sendto(bytes(decoded_answer + "\n", "utf-8"), self.client_address)
            sock_mult.close()

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 2000
    with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
        server.serve_forever()
