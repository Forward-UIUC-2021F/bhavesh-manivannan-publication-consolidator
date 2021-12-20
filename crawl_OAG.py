""" 
This program extracts professor and publication data from Microsoft Open Academic Graph (OAG) Knowledge Base.
""" 
import json
import pandas as pd
import sql_helper
import re

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
    
    sql_helper.mysql_connect()
    query = """
        SELECT title, abstract, doi, citations, authors
        FROM bm12_publications.publication_data as pd 
        WHERE (UPPER(authors) like UPPER('%""" + first_name + "%') AND UPPER(authors) like UPPER('%" +  last_name + "%')); """
    publications = sql_helper.run_query(query)
    
    if publications.shape[0] > 0:
        publications = clean_results(publications, professor)

    return publications

def clean_results(publications, professor):
    """ This function cleans the SQL results for any potential incorrect publications that may have been retrieved. E.g. A publication 
        does not contain the queried author.
    Args:
        publications (pandas dataframe): Data containing the publications' titles, authors, abstracts, and DOI's
        professor (str): Name of professor
    Returns:
        result (pandas dataframe): Data containing the proper publications' titles, authors, abstracts, and DOI's
    """
    result = publications.copy()
    for i, row in publications.iterrows():
        authors = row["authors"]
        my_regex = r"\b" + professor.lower() + r"\b"

        if re.search(my_regex, authors.lower(), re.IGNORECASE) is None: 
            result.drop(index=i, inplace = True)
    
    return result

def test_OAG():
    """Testing suite for OAG crawler"""
    publications = crawl("Jiawei Han", "University of Illinois")

    assert "Survey of Biodata Analysis from a Data Mining Perspective" in publications.values
    assert "Jiawei Han" in publications.values

    print("All OAG Crawler tests passed.")

# test_OAG()
