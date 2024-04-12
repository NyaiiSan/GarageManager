import socket
import threading

# 处理卡号
def get_id(data: bytes) -> str:
    pass

# 处理车位
def get_park(data: bytes) ->str: 
    pass

def cli_fun(sock: socket.socket):
    while 1:
        data = sock.recv(1024)
        print(data.hex(), data[0])

        if data[0] == 0xc0:
            get_id(data)
        elif data[0] == 0x0c:
            get_park(data)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(("0.0.0.0", 8777))

sock.listen()

while 1:
    cli, addr = sock.accept()
    print("new connect")
    t = threading.Thread(target=cli_fun, args=(cli,))
    t.start()

    