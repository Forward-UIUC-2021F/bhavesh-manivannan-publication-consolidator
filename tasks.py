# we are importing Celery class from celery package
from celery import Celery
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
# import crawl_gscholar
import pandas as pd

# Redis broker URL
BROKER_URL = 'redis://localhost:6380/0'

# We are creating an instance of Celery class by passing module name as Restaurant and broker as Redis.
celery_app = Celery('Restaurant', broker=BROKER_URL)

# we are decorating cooking_task function with @celery_app.task decorator.
# Functions which are decorated with @celery_app.task considered celery tasks.
@celery_app.task
def crawl_task(crawler, professor, university):
    print("Started scraping " + crawler + ": " + professor + ", " + university)

    res = None

    if crawler == "crawl_arxiv":
        res = crawl_arxiv.crawl(professor, university)
        
    elif crawler == "crawl_OAG":
        res = crawl_OAG.crawl(professor, university)

    elif crawler == "crawl_springer":
        res = crawl_springer.crawl(professor, university)

    elif crawler == "crawl_gscholar":
        """"
        res = crawl_gscholar.crawl(professor, university)
        """
        
    if res is not None:
        sql_helper.mysql_connect()
        res["citations"] = res["citations"].fillna(0)
        res["citations"] = res["citations"].astype(int)
        for x in range(1):
            for index, row in res.iterrows():
                timestamp = datetime.now()
                citations = row["citations"]
                if citations == "":
                    citations = 0

                else:
                    citations = int(citations)

                sql = "INSERT IGNORE INTO Output (timestamp, title, authors, abstract, doi, citations) VALUES (%s, %s, %s, %s, %s, %s)"
                val = (timestamp, row["title"], row["authors"], row["abstract"], row["doi"], citations)
                sql_helper.connection.cursor().execute(sql, val)

                # Connection is not autocommit by default. So you must commit to save your changes.
                sql_helper.connection.commit()

    print("Done scraping  " + crawler + ": " + professor + ", " + university)
