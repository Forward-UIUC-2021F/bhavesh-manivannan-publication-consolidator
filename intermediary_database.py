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
        # print(authors_list[x])
        if "name" in authors_list[x]:
            temp += authors_list[x]["name"]

        if (x != len(authors_list) - 1):
            temp += ", "
    return temp

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
    sql_helper.mysql_connect()

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

        for x in range(1): 
            # Insert into publications table
            citations = temp_dict["citations"]
            if citations == "":
                citations = 0

            else:
                citations = int(citations)

            sql = "INSERT IGNORE INTO publication_data (id, title, authors, abstract, doi, citations) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (temp_dict["id"], temp_dict["title"], temp_dict["authors"], temp_dict["abstract"], temp_dict["doi"], citations)
            sql_helper.connection.cursor().execute(sql, val)

            # Connection is not autocommit by default. So you must commit to save your changes.
            sql_helper.connection.commit()
    
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
    sql_helper.mysql_connect()

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

        for x in range(1):    
            # Insert into authors table
            if temp_dict["org"] != "":
                sql = ("INSERT IGNORE INTO author_data (id, name, org) VALUES (%s, %s, %s)")
                val = (temp_dict["id"], temp_dict["name"], temp_dict["org"][0])
                sql_helper.connection.cursor().execute(sql, val)
            else:
                sql = ("INSERT IGNORE INTO author_data (id, name, org) VALUES (%s, %s, %s)")
                val = (temp_dict["id"], temp_dict["name"], "")
                sql_helper.connection.cursor().execute(sql, val)

            # Insert into publication_authors table
            for x in range(len(temp_dict["pubs"])):
                sql = ("INSERT IGNORE INTO publication_author (publication_id, author_id) VALUES (%s, %s)")
                val = (temp_dict["pubs"][x]["i"], temp_dict["id"])
                sql_helper.connection.cursor().execute(sql, val)

            # Connection is not autocommit by default. So you must commit to save your changes.
            sql_helper.connection.commit()
    return authors

def test_intermediary_database():
    publication_crawler("data/oag_test.txt")
    author_crawler("data/oag_authors.txt")
    sql_helper.mysql_connect()
    df = sql_helper.run_query("SELECT * FROM publication_data;")
    assert 'Data mining: concepts and techniques' in df.values
    assert 'Jiawei Han' in df.values
    print("All intermediary database tests passed.")
  
    

# test_intermediary_database()
# test_OAG()
# publication_crawler("data/aminer_papers_1.txt")
# author_crawler("data/aminer_authors_0.txt")
# author_crawler("data/aminer_authors_1.txt")
# publications = crawl("W Whitaker", "")
# print(publications)