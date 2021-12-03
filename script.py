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
import pandas as pd

def algorithm(task):
    # Perform the crawling task. Example format on SQL Server: 'crawl_springer;Jiawei Han;University of Illinois Urbana-Champaign'
    t = task.split(';')
    if "crawl_arxiv" in t[0]:
        arxiv_publications = crawl_arxiv.crawl(t[1], t[2])
        return arxiv_publications
        
    elif "crawl_OAG" in t[0]:
        oag_publications = crawl_OAG.crawl(t[1], t[2])
        return oag_publications

    elif "crawl_springer" in t[0]:
        springer_publications = crawl_springer.crawl(t[1], t[2])
        return springer_publications

    elif "crawl_gscholar" in t[0]:
        """"
        gscholar_publications = crawl_gscholar.crawl(t[1], t[2])
        return gscholar_publications
        """
    
    return None

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
    task = ' '.join(sys.argv[1:])
    time.sleep(6)

    try:
        res = algorithm(task)
        status = 'success'
    except:
        res = '???'
        status = 'fail'
    
    sql_helper.open_ssh_tunnel()
    sql_helper.mysql_connect()
    with sql_helper.connection.cursor() as cursor:   
        for index, row in res.iterrows():
            timestamp = datetime.now()
            citations = row["citations"]
            if citations == "":
                citations = 0

            else:
                citations = int(citations)

            sql = "INSERT IGNORE INTO Output (timestamp, title, authors, abstract, doi, citations) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (timestamp, row["title"], row["authors"], row["abstract"], row["doi"], citations)
            cursor.execute(sql, val)

            # Connection is not autocommit by default. So you must commit to save your changes.
            sql_helper.connection.commit()