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
        sql_formula_all_values = f"SELECT * FROM {table}"
        self.cursor.execute(sql_formula_all_values)
        return self.cursor.fetchall()

    def get_rand_value(self, table):
        sql_formula_rand = f"SELECT * FROM {table} ORDER BY RAND() LIMIT 1"
        self.cursor.execute(sql_formula_rand)
        return self.cursor.fetchone()

    def get_name(self, short_name):
        try:
            sql_formula_name = f"SELECT * FROM persontbl WHERE shortName = '{short_name}'"
            self.cursor.execute(sql_formula_name)
            return self.cursor.fetchone()
        except:
            return "Error"

    def get_location(self, location):
        try:
            sql_formula_location = f"SELECT * FROM locationtbl WHERE shortName = '{location}'"
            self.cursor.execute(sql_formula_location)
            return self.cursor.fetchone()
        except:
            return "Error"

    def add_quote(self, quote, sayer, quoter, server, date):
        pass

    def get_list_names(self):
        pass

   def get_quotes_with_filter(self):
       pass