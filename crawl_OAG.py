""" 
This program extracts professor and publication data from Microsoft Open Academic Graph (OAG) Knowledge Base.
""" 
import json
import pandas as pd
import sql_helper

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
    
    sql_helper.open_ssh_tunnel()
    sql_helper.mysql_connect()

    query = """
        SELECT title, abstract, doi, citations, authors
        FROM bm12_publications.author_data as ad 
        INNER JOIN bm12_publications.publication_author as pa ON ad.id = pa.author_id
        INNER JOIN bm12_publications.publication_data as pd ON pa.publication_id = pd.id
        WHERE (UPPER(name) like UPPER('%""" + first_name + "%') AND UPPER(name) like UPPER('%" +  last_name + "%') AND UPPER(org) like UPPER('%" +  university + "%')); """

    publications = sql_helper.run_query(query)
    sql_helper.mysql_disconnect()
    sql_helper.close_ssh_tunnel()

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

def test_OAG():
    """Testing suite for OAG crawler"""
    publications = crawl("Jiawei Han", "University of Illinois")

    assert "Data mining: concepts and techniques" in publications.values
    assert "Jiawei Han" in publications.values

    print("All OAG Crawler tests passed.")

test_OAG()