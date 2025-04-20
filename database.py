import sqlite3
import os

class Database():
    def __init__(self):
        self.db_path = os.path.join("static", "databse.db")
        self.errors = {
            "UNIQUE constraint failed: servers.url":"This server is exist",
            "UNIQUE constraint failed: admins.username":"This username is exist",
            "UNIQUE constraint failed: configs.id":"This id is exist",
        }
        
    def set_servers(self, url:str, username:str, password:str):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DROP TABLE IF EXISTS servers
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS servers (
                    url TEXT NOT NULL UNIQUE,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                INSERT OR FAIL INTO servers (url, username, password) VALUES (?, ?, ?)
            ''', (url, username, password))
            
            conn.commit()
            conn.close()
            return {"status":True}
        except Exception as error:
            return {"status":False, "error":self.errors.get(str(error), str(error))}
        
    def get_servers(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS servers (
                    url TEXT NOT NULL UNIQUE,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            conn.commit()
            
            cursor.execute('SELECT * FROM servers')
            data = cursor.fetchall()
            conn.close()
            servers = []
            for i in data:
                servers.append({
                    "url":i[0],
                    "username":i[1],
                    "password":i[2]
                })
            
            return {"status":True, "data":servers}
        except Exception as error:
            return {"status":False, "error":str(error)}
        
    def add_admin(self, username:str, password:str, inbound_id:int):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    inbound_id INT NOT NULL,
                    wallet INT NOT NULL
                )
            ''')
            
            cursor.execute('''
                INSERT OR FAIL INTO admins (username, password, inbound_id, wallet) VALUES (?, ?, ?, ?)
            ''', (username, password, inbound_id, 0))
            
            conn.commit()
            conn.close()
            return {"status":True}
        except Exception as error:
            return {"status":False, "error":self.errors.get(str(error), str(error))}
        
    def edit_admin(self, username:str, password:str, inbound_id:int):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f'UPDATE admins SET password = "{password}", inbound_id = {inbound_id} WHERE username = "{username}"')
            
            conn.commit()
            conn.close()
            return {"status":True}
        except Exception as error:
            return {"status":False, "error":self.errors.get(str(error), str(error))}
        
    def get_admins(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    inbound_id INT NOT NULL,
                    wallet INT NOT NULL
                )
            ''')
            conn.commit()
            
            cursor.execute('SELECT * FROM admins')
            data = cursor.fetchall()
            conn.close()
            admins = []
            for i in data:
                admins.append({
                    "id":i[0],
                    "username":i[1],
                    "password":i[2],
                    "inbound_id":i[3],
                    "wallet":i[4],
                })
            
            return {"status":True, "data":admins}
        except Exception as error:
            return {"status":False, "error":str(error)}
        
    def login_admin(self, username, password):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    inbound_id INT NOT NULL,
                    wallet INT NOT NULL
                )
            ''')
            conn.commit()
            cursor.execute(f'SELECT * FROM admins WHERE username = "{username}"')
            data = cursor.fetchall()
            conn.close()
            if len(data) > 0:
                if data[0][2] == password:
                    return {"status":True, "data":{"id":data[0][0]}}
                else:
                    return {"status":False, "error":"Password not match"}
            else:
                return {"status":False, "error":"Username not exist"}
            
        except Exception as error:
            return {"status":False, "error":str(error)}
        
    def get_admins_wallet(self, id:int):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    inbound_id INT NOT NULL,
                    wallet INT NOT NULL
                )
            ''')
            conn.commit()
            
            cursor.execute(f'SELECT wallet FROM admins WHERE id = {id}')
            data = cursor.fetchone()
            conn.close()
            
            return {"status":True, "data":{"wallet":data[0]}}
        except Exception as error:
            return {"status":False, "error":str(error)}
        
    def get_admins_inbound_id(self, id:int):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    inbound_id INT NOT NULL,
                    wallet INT NOT NULL
                )
            ''')
            conn.commit()
            
            cursor.execute(f'SELECT inbound_id FROM admins WHERE id = {id}')
            data = cursor.fetchone()
            conn.close()
            
            return {"status":True, "data":{"inbound_id":data[0]}}
        except Exception as error:
            return {"status":False, "error":str(error)}
        
    def add_admin_wallet(self, id:int, price:int):
        try:
            wallet = self.get_admins_wallet(id).get("data")["wallet"]
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    inbound_id INT NOT NULL,
                    wallet INT NOT NULL
                )
            ''')
            conn.commit()
            
            cursor.execute(f'UPDATE admins SET wallet = {wallet + price} WHERE id = {id}')
            conn.commit()
            conn.close()
            
            return {"status":True}
        except Exception as error:
            return {"status":False, "error":self.errors.get(str(error), str(error))}
        
    def add_config(self, id:str, username:str, inbound_id:int, admin_id:int):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configs (
                    id TEXT NOT NULL UNIQUE,
                    username TEXT NOT NULL,
                    inbound_id INT NOT NULL,
                    admin_id INT NOT NULL
                )
            ''')
            
            cursor.execute('''
                INSERT OR FAIL INTO configs (id, username, inbound_id, admin_id) VALUES (?, ?, ?, ?)
            ''', (id, username, inbound_id, admin_id))
            
            conn.commit()
            conn.close()
            
            return {"status":True}
        except Exception as error:
            return {"status":False, "error":self.errors.get(str(error), str(error))}
        
    def get_admins_configs(self, admin_id:int):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configs (
                    id TEXT NOT NULL UNIQUE,
                    username TEXT NOT NULL,
                    inbound_id INT NOT NULL,
                    admin_id INT NOT NULL
                )
            ''')
            conn.commit()
            
            cursor.execute(f'SELECT * FROM configs WHERE admin_id = {admin_id}')
            data = cursor.fetchall()
            conn.close()
            configs = []
            for i in data:
                configs.append({
                    "id":i[0],
                    "username":i[1],
                    "inbound_id":i[2]
                })
            return {"status":True, "data":configs}
        except Exception as error:
            return {"status":False, "error":str(error)}
        
    def add_new(self, new:str):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news (
                    new TEXT NOT NULL
                )
            ''')
            
            cursor.execute(f'INSERT OR FAIL INTO news (new) VALUES ("{new}")')
            
            conn.commit()
            conn.close()
            
            return {"status":True}
        except Exception as error:
            return {"status":False, "error":self.errors.get(str(error), str(error))}
        
    def get_new(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news (
                    new TEXT NOT NULL
                )
            ''')
            conn.commit()
            
            cursor.execute(f'SELECT new FROM news')
            data = cursor.fetchall()
            conn.close()
            
            if len(data) > 0:
                return {"status":True, "data":{"new":data[-1][0]}}
            else:
                return {"status":True, "data":{"new":""}}
        except Exception as error:
            return {"status":False, "error":str(error)}
        
    def update_user(self, user_id, inbound_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configs (
                    id TEXT NOT NULL UNIQUE,
                    username TEXT NOT NULL,
                    inbound_id INT NOT NULL,
                    admin_id INT NOT NULL
                )
            ''')
            
            conn.commit()
            
            cursor.execute(f'UPDATE configs SET inbound_id = "{inbound_id}" WHERE id = "{user_id}"')
            conn.commit()
            conn.close()
            
            return {"status":True}
        except Exception as error:
            return {"status":False, "error":self.errors.get(str(error), str(error))}
        
    def add_report(self, admin_id:int, operation:str, operation_price:int,wallet_after_operation:int, wallet_before_operation:int):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    admin_id INT NOT NULL,
                    operation TEXT NOT NULL,
                    operation_price INT NOT NULL,
                    wallet_after_operation INT NOT NULL,
                    wallet_before_operation INT NOT NULL
                )
            ''')
            
            cursor.execute('''
                INSERT OR FAIL INTO reports (admin_id, operation, operation_price, wallet_after_operation, wallet_before_operation) VALUES (?, ?, ?, ?, ?)
            ''', (admin_id, operation, operation_price, wallet_after_operation, wallet_before_operation))
            
            conn.commit()
            conn.close()
            return {"status":True}
        except Exception as error:
            return {"status":False, "error":self.errors.get(str(error), str(error))}
        
    def get_admins_report(self, admin_id:int):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    admin_id INT NOT NULL,
                    operation TEXT NOT NULL,
                    operation_price INT NOT NULL,
                    wallet_after_operation INT NOT NULL,
                    wallet_before_operation INT NOT NULL
                )
            ''')
            
            conn.commit()
            
            cursor.execute('SELECT * FROM reports WHERE admin_id = ?', (admin_id,))
            data = cursor.fetchall()
            conn.close()
            reports = []
            for i in data:
                reports.append([i[1], i[2], i[4], i[3]])
            
            return {"status":True, "data":{"reports":reports}}
        except Exception as error:
            return {"status":False, "error":str(error)}

# db = Database()

# print(db.update_user("00000005-16f9-40db-b610-5d9ca51d3c23", 6, "vless://00000005-16f9-40db-b610-5d9ca51d3c23@www.x8ss0.com:2052?type=ws&path=%2FV2ray%3Fed%3D443&host=#New test"))