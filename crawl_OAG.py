""" 
This program extracts professor and publication data from Microsoft Open Academic Graph (OAG) Knowledge Base.
""" 
import json
import pandas as pd
import pymysql
import logging
import sshtunnel
from sshtunnel import SSHTunnelForwarder

def contains_professor(authors_list, professor):
    """Checks if the given professor is one of the authors of the publication.

    Args:
        authors_list (list): List of authors from OAG
        professor (str): Name of professor

    Returns:
        True (bool): Professor is one of the authors
        False (bool): Professor is not one of the authors

    """
    for x in authors_list: # authors_list example: "authors": [{"name": "John Smith", "id": "2404364408"}]"
        if "name" in x:
            if professor.lower() in x["name"].lower():
                return True
    
    return False

def authors_to_string(authors_list):
    """Converts list of OAG authors into a comma separated string.

    Args:
        authors_list (list): List of authors from OAG

    Returns:
        temp (str): Comma separated string of all the creators

    """
    temp = ""
    for x in range(len(authors_list)):
        temp += authors_list[x]["name"]

        if (x != len(authors_list) - 1):
            temp += ", "
    return temp

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
    open_ssh_tunnel()
    mysql_connect()

    query = """
        SELECT title, abstract, doi, citations, authors
        FROM bm12_publications.author_data as ad 
        INNER JOIN bm12_publications.publication_author as pa ON ad.id = pa.author_id
        INNER JOIN bm12_publications.publication_data as pd ON pa.publication_id = pd.id
        WHERE (UPPER(name) like UPPER('%""" + first_name + "%') AND UPPER(name) like UPPER('%" +  last_name + "%') AND UPPER(org) like UPPER('%" +  university + "%')); """

    publications = run_query(query)
    mysql_disconnect()
    close_ssh_tunnel()

    return publications

def publication_crawler(file):
    """Crawler helper function that crawls data for publications
    Args:
        file (str): Path of file

    Returns:
        publications (pandas dataframe): Data containing the publications' titles, authors, abstracts, and DOI's

    """
    # Initialization
    column_names = ["id", "title", "authors", "abstract", "doi", "citations"]
    publications = pd.DataFrame(columns = column_names)

    # Check for empty file path
    if file == "":
        return publications

    # Open file
    file_papers = open(file, 'r')

    # Loop through file.
    while True:
        # Get next line from file
        line = file_papers.readline()
    
        # If line is empty end of file is reached
        if not line:
            break

        # Load the line into json
        pub_json = json.loads(line)
        temp_dict = {}   

        if "authors" in pub_json:
            temp_dict["authors"] = authors_to_string(pub_json["authors"])
        else:
            temp_dict["authors"] = ""

        if "id" in pub_json:
            temp_dict["id"] = pub_json["id"]
        else:
            temp_dict["id"] = ""

        if "title" in pub_json:
            temp_dict["title"] = pub_json["title"]
        else:
            temp_dict["title"] = ""
            
        if "abstract" in pub_json:
            temp_dict["abstract"] = pub_json["abstract"]
        else:
            temp_dict["abstract"] = ""
            
        if "doi" in pub_json:
            temp_dict["doi"] = pub_json["doi"]
        else:
            temp_dict["doi"] = ""
            
        if "citations" in pub_json:
            temp_dict["citations"] = pub_json["n_citation"]
        else:
            temp_dict["citations"] = ""
            
        publications = publications.append(temp_dict, ignore_index=True)
    
    return publications

def author_crawler(file):
    """Crawler helper function that crawls data for authors from a file

    Args:
        file (str): Path of file

    Returns:
        authors (pandas dataframe): Data containing the authors' id, name, and organization

    """

    # Initialization
    column_names = ["id", "name", "org", "pubs"]
    authors = pd.DataFrame(columns = column_names)

    # Check for empty file path
    if file == "":
        return authors

    # Open file
    file_papers = open(file, 'r')

    # Loop through file.
    while True:
        # Get next line from file
        line = file_papers.readline()
    
        # If line is empty end of file is reached
        if not line:
            break

        # Load the line into json
        author_json = json.loads(line)
        temp_dict = {}   

        if "id" in author_json:
            temp_dict["id"] = author_json["id"]

        else:
            temp_dict["id"] = ""

        if "name" in author_json:
            temp_dict["name"] = author_json["name"]

        else:
            temp_dict["name"] = ""

        if "orgs" in author_json:
            temp_dict["org"] = author_json["orgs"]

        else:
            temp_dict["org"] = ""

        if "pubs" in author_json:
            temp_dict["pubs"] = author_json["pubs"]

        else:
            temp_dict["pubs"] = ""
            
        authors = authors.append(temp_dict, ignore_index=True)
    
    return authors

def open_ssh_tunnel(verbose=False):
    """Open an SSH tunnel and connect using a username and password.
    
    Args:
      verbose(bool): Set to True to show logging

    Returns: 
      tunnel: Global SSH tunnel connection
    """
    # SSH Information
    ssh_host = 'Owl2.cs.illinois.edu'
    ssh_user = 'bm12'

    # Load SSH password from file
    text_file = open("ssh_password.txt", "r")
    ssh_pass = text_file.read()
    text_file.close()

    if verbose:
        sshtunnel.DEFAULT_LOGLEVEL = logging.DEBUG
    
    global tunnel
    tunnel = SSHTunnelForwarder(
        (ssh_host, 22),
        ssh_username = ssh_user,
        ssh_password = ssh_pass,
        remote_bind_address = ('127.0.0.1', 3306)
    )
    
    tunnel.start()

def mysql_connect():
    """Connect to a MySQL server using the SSH tunnel connection
    
    Returns: 
      connection: Global MySQL database connection
    """
    # Database Credentials
    db_host = '127.0.0.1'
    db_name = "bm12_publications"
    db_user = "bm12"

    # Load database password from file
    text_file = open("db_password.txt", "r")
    db_password = text_file.read()
    text_file.close()

    global connection
    
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        passwd=db_password,
        db=db_name,
        port=tunnel.local_bind_port
    )

def run_query(sql):
    """Runs a given SQL query via the global database connection.
    
    Args:
      sql: MySQL query
    
    Returns: 
      Pandas dataframe containing results
    """
    
    return pd.read_sql_query(sql, connection)

def mysql_disconnect():
    """Closes the MySQL database connection.
    """
    connection.close()

def close_ssh_tunnel():
    """Closes the SSH tunnel connection.
    """
    tunnel.close

def test_OAG():
    """Testing suite for OAG crawler"""
    publications = crawl("Jiawei Han", "University of Illinois")

    assert "Data mining: concepts and techniques" in publications.values
    assert "Jiawei Han" in publications.values

    print("All OAG Crawler tests passed.")

test_OAG()