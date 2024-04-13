import sqlite3
import hashlib

class DataBase:

    file_path = None

    def __init__(self, path: str) -> None:
        self.file_path = path
        with sqlite3.connect(path) as con:
            cur = con.cursor()
            # 删除表
            cur.execute("DROP TABLE IF EXISTS users;")
            # 创建用户表
            cur.execute("""CREATE TABLE IF NOT EXISTS users(
                        id      text    PRIMARY KEY,
                        passwd  text    NOT NULL,
                        car     text    NOT NULL,
                        name    text    NOT NULL,
                        phone   text    NOT NULL,
                        state   boolean,
                        wallet  float
                        );""")
            
            # 用户默认密码
            dpasswd = 'e10adc3949ba59abbe56e057f20f883e'
            # 添加用户
            cur.execute("INSERT INTO USERS (id, passwd, car, name, phone) VALUES(?, ?, ?, ?, ?);", ("3D985A8C", dpasswd, "A78A54", "沈华强", "13988776655"))
            cur.execute("INSERT INTO USERS (id, passwd, car, name, phone) VALUES(?, ?, ?, ?, ?);", ("334455AA", dpasswd, "D123A5", "彩须坤", "13088226655"))

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
        
# 实例化数据库对象
db = DataBase("data.db")