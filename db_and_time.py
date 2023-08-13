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

class Time:
    def __init__(self):
        self.avg_time = 0
        self.total_time = 0  # Total time it took to put a block
        self.start_time = 0  # Time when the block was first created

    def update_time(self, time: float, block_count: int):
        self.total_time += (time - self.start_time)
        self.avg_time = self.total_time / block_count



    