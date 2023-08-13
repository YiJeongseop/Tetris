import os
import sqlite3  # https://docs.python.org/3.8/library/sqlite3.html
from settings import DB_PATH, DB_NAME

class DB:
    def __init__(self):
        if os.path.isfile(DB_PATH) is not True:
            self.con = sqlite3.connect(DB_NAME)  # Create Connection Object
            self.cur = self.con.cursor()  # You must create a Cursor Object before execute()
            self.cur.execute("CREATE TABLE HighestScore (Score, AverageTimeToPutABlock)")
            self.cur.execute("INSERT INTO HighestScore (Score, AverageTimeToPutABlock) VALUES (0, 0)")  # and insert 0, 0
            self.con.commit()  # Save (commit) the changes
        else:
            self.con = sqlite3.connect(DB_NAME)
            self.cur = self.con.cursor()
    
    def fetch_highest_score(self) -> list:     
        self.cur.execute("SELECT * FROM HighestScore ORDER BY Score DESC")
        return self.cur.fetchall()  # Fetches all (remaining) rows of a query result, returning a list

    def save_highest_score(self, score: int, avg_time: float):
        self.cur.execute(f"INSERT INTO HighestScore VALUES ({score}, {avg_time})")
        self.con.commit()


    