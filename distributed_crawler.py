"""
This module is the Distributed Crawler Management Module that performs scraping tasks from 
existing knowledge bases (e.g. MAG, OAG) asynchronously through the user of workers and stores data 
into a unified database for the EducationToday website. The scraping tasks can be found in tasks.py
"""

from tasks import crawl_task
from celery import Celery
from celery.result import AsyncResult
import mysql.connector
import sql_helper
from datetime import datetime
import pandas as pd
import consolidator

def crawl(professor, university):
    # Create Output Table
    sql_helper.mysql_connect()
    sql_helper.connection.cursor().execute("DROP TABLE IF EXISTS output_publications")
    sql_helper.connection.cursor().execute("CREATE TABLE `output_publications` (`id` bigint(255) NOT NULL AUTO_INCREMENT,`timestamp` varchar(100) CHARACTER SET latin1 DEFAULT NULL,`title` varchar(3000) DEFAULT NULL,`authors` varchar(3072) DEFAULT NULL,`abstract` varchar(3072) DEFAULT NULL,`knowledge_base` varchar(3072) DEFAULT NULL,`doi` varchar(3072) DEFAULT NULL,`citations` int(11) DEFAULT NULL,PRIMARY KEY (`id`))")

    # Arxiv Task
    arxiv = crawl_task.delay("crawl_arxiv", professor, university)
    print("Arxiv Task ID: ", arxiv)

    # Springer Task
    springer = crawl_task.apply_async(args=["crawl_springer", professor, university])
    print("Springer Task ID: ", springer)

    # OAG Task
    oag = crawl_task.apply_async(args=["crawl_oag", professor, university])
    print("OAG Task ID: ", oag)

    # GScholar Task
    # gscholar = crawl_task.apply_async(args=["crawl_gscholar", professor, university])
    # print(gscholar)

    # Check if the tasks are done running
    while (arxiv.status != "SUCCESS" or springer.status != "SUCCESS" or oag.status != "SUCCESS"):
        continue
    
    # All the tasks are done running, consolidate data in the output_publications database table and send to final_publications table.
    if (arxiv.status == "SUCCESS" and springer.status == "SUCCESS" and oag.status == "SUCCESS"):
        print("All Tasks Done")
        consolidator.consolidate()


# crawl("Jiawei Han", "University of Illinois Urbana-Champaign")
crawl("Pieter Abbeel", "University of California Berkeley") # Contains Duplicates from Springer + Arxiv