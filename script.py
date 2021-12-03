import mysql.connector
import sql_helper
import sys
import json
import os
from datetime import datetime
import time
import crawl_OAG
import crawl_arxiv
import crawl_springer
import crawl_gscholar

def algorithm(task):
    t = task.split(' plus ')
    return int(t[0]) + int(t[1])

if __name__ == "__main__":
    """
    mydb = mysql.connector.connect(
        host="owl2.cs.illinois.edu",
        user="bm12",
        password="publications123",
        database="bm12_publications"
    )
    mycursor = mydb.cursor()
    """
    sql_helper.open_ssh_tunnel()
    sql_helper.mysql_connect()

    task = ' '.join(sys.argv[1:])
    time.sleep(6)

    try:
        res = algorithm(task)
        status = 'success'
    except:
        res = '???'
        status = 'fail'

    with sql_helper.connection.cursor() as cursor:   
        for index, row in publications.iterrows():
            timestamp = datetime.now()
            citations = row["citations"]
            if citations == "":
                citations = 0

            else:
                citations = int(citations)

            sql = "INSERT IGNORE INTO Output (timestamp, title, authors, abstract, doi, citations) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (row["title"], row["authors"], row["abstract"], row["doi"], citations)
            cursor.execute(sql, val)

            # Connection is not autocommit by default. So you must commit to save your changes.
            sql_helper.connection.commit()
