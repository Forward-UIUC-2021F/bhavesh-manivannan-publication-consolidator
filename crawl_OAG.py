""" 
This program extracts professor and publication data from Microsoft Open Academic Graph (OAG) Knowledge Base.
""" 
import json
import pandas as pd
import sql_helper

def crawl(professor, university):
    """Crawls OAG knowledge base for publications associated with the professor from the specified university.

    Args:
        professor (str): Name of professor
        university (str): Name of university

    Returns:
        publications (pandas dataframe): Data containing the publications' titles, authors, abstracts, and DOI's

    """
    first_name = professor.split(" ")[0]
    last_name = professor.split(" ")[1]
    
    sql_helper.open_ssh_tunnel()
    sql_helper.mysql_connect()

    query = """
        SELECT title, abstract, doi, citations, authors
        FROM bm12_publications.author_data as ad 
        INNER JOIN bm12_publications.publication_author as pa ON ad.id = pa.author_id
        INNER JOIN bm12_publications.publication_data as pd ON pa.publication_id = pd.id
        WHERE (UPPER(name) like UPPER('%""" + first_name + "%') AND UPPER(name) like UPPER('%" +  last_name + "%') AND UPPER(org) like UPPER('%" +  university + "%')); """

    publications = sql_helper.run_query(query)
    return publications

def test_OAG():
    """Testing suite for OAG crawler"""
    publications = crawl("Jiawei Han", "University of Illinois")

    assert "Data mining: concepts and techniques" in publications.values
    assert "Jiawei Han" in publications.values

    print("All OAG Crawler tests passed.")

test_OAG()
