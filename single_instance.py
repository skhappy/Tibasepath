import socket
import sys

class SingleInstance:
    def __init__(self, port=12721):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind(('localhost', self.port))
            self.sock.listen(1)
        except socket.error:
            sys.exit(0)  # 如果端口被占用，说明已经有实例在运行，直接退出

    def __del__(self):
        try:
            self.sock.close()
        except:
            pass 