import socket
import threading
import time

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
                # 验证数据
                if data[5] != 0xc0:
                    print("Wrong data")

                userid = data.hex()[2:2+8]
                print("id: ", userid)
                # 获取车辆信息
                car_info = db.get_car_byID(userid)
                # 判断用户车辆状态
                if car_info['state'] == True: # 车辆状态为True, 表示本次为出库
                    # 计算停车时间
                    park_time = int(time.time()) - car_info['times']
                    print("park time: ", park_time)
                    # 计算费用
                    spent = park_time * 0.5
                    db.spend(userid, spent)
                    sock.send(("Time: %d\nSpent: %.2f"%(park_time, spent)).encode())
                    db.car_out(userid)
                else: # 车辆状态为False, 表示本次为入库
                    sock.send(("Welecomes\n" + car_info['car']).encode())
                    db.car_in(userid)


            elif data[0] == 0x0c: # 获取到的是车位信息
                print("Get parking", data.hex())
                for i in range(1, len(data)):
                    if data[i] == 0x0c:
                        break
                    state = True if data[i] == 49 else False
                    db.update_park("A" + str(i-1), state)

            else:
                print(data.decode())


# 打开硬件接口
esp = Interface()
esp.run()