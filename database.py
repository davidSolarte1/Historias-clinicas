import hashlib
import mysql.connector

# MYSQL_CFG = {
#     "host": "172.20.100.141",   
#     "user": "sireh_user",
#     "password": "sireh27082025",
#     "database": "sireh_db",
#     "autocommit": False,
#}
MYSQL_CFG = {
    "host": "127.0.0.1",   
    "user": "root   ",
    "password": "admin",
    "database": "sireh_db",
    "autocommit": False,
}

def get_connection():
    return mysql.connector.connect(**MYSQL_CFG)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


