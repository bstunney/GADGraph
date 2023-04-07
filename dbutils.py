"""
filename: dbutils.py
Requires the driver:  conda install mysql-connector-python

description: A collection of database utilities to make it easier
to implement a database application
"""

import mysql.connector
import pandas as pd

class DBUtils:

    def __init__(self, user, password, database, host="localhost"):
        """ Future work: Implement connection pooling """
        self.con = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

    def close(self):
        """ Close or release a connection back to the connection pool """
        self.con.close()
        self.con = None

    def execute(self, query, df=False):
        """ Execute a select query and returns the result as a dataframe """
        rs = self.con.cursor()
        rs.execute(query)
        rows = rs.fetchall()
        cols = list(rs.column_names)
        rs.close()
        # returns df if set to true for results
        if df == True:
            return pd.DataFrame(rows, columns=cols)


    def insert_one(self, sql, val):
        """ Insert a single row """
        cursor = self.con.cursor()
        cursor.execute(sql, val)
        self.con.commit()


    def insert_many(self, sql, vals):
        """ Insert multiple rows """
        cursor = self.con.cursor()
        cursor.executemany(sql, vals)
        self.con.commit()