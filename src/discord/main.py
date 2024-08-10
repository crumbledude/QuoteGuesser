import discord
from common.db_connector import Db
import os
from dotenv import find_dotenv, load_dotenv

#Load environment variables
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

TEST_DB_IP = os.getenv("TEST_DB_IP")
TEST_DB_USER = os.getenv("TEST_DB_USER")
TEST_DB_PASS = os.getenv("TEST_DB_PASS")
REAL_DB_IP = os.getenv("REAL_DB_IP")
REAL_DB_USER = os.getenv("REAL_DB_USER")
REAL_DB_PASS = os.getenv("REAL_DB_PASS")

def main():
    #test_db = Db(TEST_DB_IP, "25576", TEST_DB_USER, TEST_DB_PASS, "testdb")
    # print(test_db.get_all_values('students'))
    # print(test_db.get_rand_value("students"))
    actuall_db = Db(REAL_DB_IP, "3306", REAL_DB_USER, REAL_DB_PASS, "quotedb")
    print(actuall_db.get_rand_value("quotetbl"))


if __name__ == '__main__':
    main()