import sqlite3
import hashlib
import random

class DataBase:

    file_path = None

    def __init__(self, path: str) -> None:
        self.file_path = path
        with sqlite3.connect(path) as con:
            cur = con.cursor()
            # 初始化用户表
            cur.execute("DROP TABLE IF EXISTS users;") # 删除旧表
            # 创建新用户表
            cur.execute("""CREATE TABLE IF NOT EXISTS users(
                        id      text    PRIMARY KEY,
                        passwd  text    NOT NULL,
                        car     text    NOT NULL,
                        name    text    NOT NULL,
                        phone   text    NOT NULL,
                        state   boolean,
                        wallet  float,
                        times   int
                        );""")
            
            # 用户默认密码
            dpasswd = 'e10adc3949ba59abbe56e057f20f883e'
            # 添加用户
            cur.execute("INSERT INTO USERS (id, passwd, car, name, phone, state, wallet, times) \
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?);", ("36606b60", dpasswd, "A78A54", "沈华强", "13988776655", False, random.randint(1000, 9999)/100, -1))
            cur.execute("INSERT INTO USERS (id, passwd, car, name, phone, state, wallet, times) \
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?);", ("e3f6e22e", dpasswd, "D123A5", "彩须坤", "13088226655", False, random.randint(1000, 9999)/100, -1))

            # 初始化车位表
            cur.execute("DROP TABLE IF EXISTS parks;") # 删除旧车位表
            cur.execute("""CREATE TABLE IF NOT EXISTS parks(
                        id      text        PRIMARY KEY,
                        state   boolean     NOT NULL,
                        zone    text        NOT NULL
                        );""")
            
            # 添加车位
            # A区
            for i in range(3):
                cur.execute("INSERT INTO PARKS (id, state, zone) VALUES(?, ?, ?);", (f"A{i}", False, "A"))
            # B区
            for i in range(8):
                cur.execute("INSERT INTO PARKS (id, state, zone) VALUES(?, ?, ?);", (f"B{i}", random.choice([True, False]), "B"))
            # C区
            for i in range(8):
                cur.execute("INSERT INTO PARKS (id, state, zone) VALUES(?, ?, ?);", (f"C{i}", random.choice([True, False]), "C"))
            # D区
            for i in range(8):
                cur.execute("INSERT INTO PARKS (id, state, zone) VALUES(?, ?, ?);", (f"D{i}", random.choice([True, False]), "D"))
            # E区
            for i in range(8):
                cur.execute("INSERT INTO PARKS (id, state, zone) VALUES(?, ?, ?);", (f"E{i}", random.choice([True, False]), "E"))
            

    def add_user(user: dict) -> bool:
        pass

    # 获取所有用户数据
    def get_all_users(self) -> tuple[dict]:
        pass

    # 根据ID获取一个用户的基本数据
    def get_user_byID(self, id: str) -> dict:
        user = dict()
        with sqlite3.connect(self.file_path) as con:
            cur = con.cursor()
            res = cur.execute("SELECT id, car, name, phone FROM users WHERE id = ?;", (id,))
            for row in res:
                user["id"] = row[0]
                user["car"] = row[1]
                user["name"] = row[2]
                user["phone"] = row[3]
        return user
    
    # 根据id获取一个用户的车牌号
    def get_car_byID(self, id: str) -> str:
        car = ""
        with sqlite3.connect(self.file_path) as con:
            cur = con.cursor()
            res = cur.execute("SELECT car FROM users WHERE id = ?;", (id,))
            for row in res:
                car = row[0]
        return car

    # 修改用户的基本信息
    def chuser_info(self, id: str, username: str, car: str, phone: str) -> int:
        with sqlite3.connect(self.file_path) as con:
            cur = con.cursor()
            cur.execute("UPDATE USERS SET name = ? WHERE id = ?;", (username, id))
            cur.execute("UPDATE USERS SET car = ? WHERE id = ?;", (car, id))
            cur.execute("UPDATE USERS SET phone = ? WHERE id = ?;", (phone, id))

    # 验证用户登录信息
    def check_user(self, id: str, passwd: str) -> int:
        # 从数据库中读取用户信息
        result = None
        with sqlite3.connect(self.file_path) as con:
            cur = con.cursor()
            cur.execute("SELECT passwd FROM users WHERE id = ?;", (id,))
            result = cur.fetchone()
        # 判断用户是否在数据库中
        if result == None:
            return -1
        # 判断密码是否正确
        elif result[0] == hashlib.md5(passwd.encode("utf-8")).hexdigest():
            return 1
        else:
            return 0
    
    # 获取用户钱包状态
    def get_user_wallet(self, userid: str) -> dict:
        wallet = dict()
        wallet['id'] = userid
        with sqlite3.connect(self.file_path) as con:
            cur = con.cursor()
            res = cur.execute("SELECT wallet, times FROM users WHERE id = ?;", (userid,))
            for row in res:
                wallet['wallet'] = row[0]
                wallet['times'] = row[1]
        return wallet
    
    # 用户充值
    def topup(self, userid, amount):
        try:
            with sqlite3.connect(self.file_path) as con:
                cur = con.cursor()
                cur.execute("UPDATE USERS SET wallet = wallet + ? WHERE id = ?;", (amount, userid))
            return 1
        except Exception as e:
            print(e)
            return 0
        
    def get_parks(self, zone: str) -> list[int]:
        parks = list()
        with sqlite3.connect(self.file_path) as con:
            cur = con.cursor()
            res = cur.execute("SELECT state FROM parks WHERE zone = ?;", (zone,))
            for row in res:
                parks += (row[0],)
        return parks

    # 更新车位状态
    def update_park(self, id: str, state: bool) -> int:
        with sqlite3.connect(self.file_path) as con:
            cur = con.cursor()
            cur.execute("UPDATE PARKS SET state = ? WHERE id = ?;", (state, id))
            return 1

# 实例化数据库对象
db = DataBase("data.db")
