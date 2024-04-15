import socket
import threading

from database import db

class Interface:
    ip = "0.0.0.0"
    port = 8777
    sock = None

    def __init__(self) -> None:
        # 创建链接socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip, self.port))
        self.sock = sock

    def run(self):
        t = threading.Thread(target=self.start_interface, daemon=True)
        t.start()
            
    def start_interface(self):
        print("Start interface")
        sock = self.sock
        sock.listen(5)
        while 1:
            cli, addr = sock.accept()
            print("new connect", addr)
            t = threading.Thread(target=self.cli_fun, args=(cli,), daemon=True)
            t.start()

    def cli_fun(self, sock: socket.socket):
        while 1:
            data = sock.recv(1024)
            if data[0] == 0xc0: # 获取到的是用户id信息
                print("Get id", data.hex())
                car = db.get_car_byID(data.hex()[2:2+8])
                sock.send(car.encode())

            elif data[0] == 0x0c: # 获取到的是车位信息
                print("Get parking", data.hex())
                for i in range(1, len(data)):
                    if data[i] == 0x0c:
                        break
                    state = True if data[i] == 49 else False
                    db.update_park("A" + str(i-1), state)

# 打开硬件接口
esp = Interface()
esp.run()