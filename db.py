import os
import sqlite3
from settings import DB_PATH, DB_NAME

class DB:
    def __init__(self):
        """
        if DB file does not exist, create it and connect it.
        if it exists, connect it.
        """
        if os.path.isfile(DB_PATH) is not True:
            self.con = sqlite3.connect(DB_NAME) 
            self.cur = self.con.cursor() 
            self.cur.execute("CREATE TABLE HighestScore (Score, AverageTimeToPutABlock)")
            self.cur.execute("INSERT INTO HighestScore (Score, AverageTimeToPutABlock) VALUES (0, 0)")
            self.con.commit()
        else:
            self.con = sqlite3.connect(DB_NAME)
            self.cur = self.con.cursor()
    
    def fetch_highest_score(self) -> list:
        """
        Fetches all rows of a query result, Return it as list.
        """     
        self.cur.execute("SELECT * FROM HighestScore ORDER BY Score DESC")
        return self.cur.fetchall()

    def save_highest_score(self, score: int, avg_time: float):
        """
        Save to DB the score and average time to put a block.
        """
        self.cur.execute(f"INSERT INTO HighestScore VALUES ({score}, {avg_time})")
        self.con.commit()



    