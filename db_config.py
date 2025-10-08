# db_config.py
from flask_mysqldb import MySQL

def init_db(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''  # ถ้ามีรหัสให้ใส่
    app.config['MYSQL_DB'] = 'diabetes_db'  # ชื่อฐานข้อมูล
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # ส่งข้อมูลเป็น dict
    mysql = MySQL(app)
    return mysql