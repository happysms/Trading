import pymysql

class MariaDB:
    def __init__(self):
        """mariaDB 연결"""
        self.conn = pymysql.connect(host="cryptocurrencydatabase.c5h79dp2k6f7.ap-northeast-2.rds.amazonaws.com",
                                    user="admin",
                                    password="khuminsung12!",
                                    db="trading",
                                    charset="utf8")

