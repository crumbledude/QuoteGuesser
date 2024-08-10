import mysql.connector

class Db:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

        self.mydb = mysql.connector.connect(
            host = self.host,
            port = self.port,
            user = self.user,
            password = self.password,
            database = self.database
        )

        self.cursor = self.mydb.cursor()

    def get_all_values(self, table):
        sql_formula = f"SELECT * FROM {table}"
        self.cursor.execute(sql_formula)
        return self.cursor.fetchall()

    def get_rand_value(self, table):
        sql_formula = f"SELECT * FROM {table} ORDER BY RAND()"
        self.cursor.execute((sql_formula))
        return self.cursor.fetchone()
