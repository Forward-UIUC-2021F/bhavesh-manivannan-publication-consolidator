"""
This module works very closely with the Distributed Crawler Management Module (in fact, you could 
consider them acting as a singular module) to aggregate information from scraping tasks and from 
existing knowledge bases (e.g. MAG, OAG) into a unified database for the EducationToday website.  
Note that this module does not handle ranking or keyword assignment related data. It only handles 
core data: descriptive data of each entity (e.g. research position of an author, number of citations 
for a publication) and core linking relations between each entity (e.g. current institution of professors).
"""

import crawl_gscholar as gscholar
import crawl_OAG as oag
import crawl_arxiv as arxiv
import crawl_springer as springer
import pandas as pd
import json
import sql_helper

def consolidate():
    """ Handles overlaps and conflicting information from the different knowledge bases. The 
        final data is uploaded into a final_publications table on the database.
    """
    # Pull data from output_publications table and store in publications dataframe
    sql_helper.mysql_connect()
    query = "SELECT * FROM bm12_publications.output_publications;"
    publications = sql_helper.run_query(query)
    publications_titles = publications.copy()
    result = publications.copy()
    
    # Lowercase the titles in the dataframe 
    publications["title"] = publications["title"].str.lower()

    # Remove duplicates by checking for publications that have similar titles
    duplicates = publications[publications.duplicated('title')]

    # Loop through duplicates dataframe
    for index, row in duplicates.iterrows():
        # Generate list containing indices of the rows containing the specified "duplicate" title
        title = row["title"]
        indices = publications.index[publications['title'] == title].to_list()
        temp_dict = {}
        temp_dict["id"] = row["id"]
        temp_dict["timestamp"] = row["timestamp"]
        temp_dict["title"] = row["title"]
        temp_dict["authors"] = row["authors"]
        temp_dict["abstract"] = row["abstract"]
        temp_dict["knowledge_base"] = row["knowledge_base"]
        temp_dict["doi"] = row["doi"]
        temp_dict["citations"] = row["citations"]

        # Loop through indice list and consolidate data.
        for x in indices:
            current = publications_titles.iloc[[x]]
            temp_dict["title"] = current["title"].values[0]

            # Check if authors list is longer
            if temp_dict["authors"] is not None and current["authors"].values[0] is not None and len(temp_dict["authors"]) < len(current["authors"].values[0]):
                temp_dict["authors"]  = current["authors"].values[0]
                temp_dict["knowledge_base"] = current["knowledge_base"].values[0]

            # Check if abstract is longer
            if temp_dict["abstract"] is not None and current["abstract"].values[0] is not None and len(temp_dict["abstract"]) < len(current["abstract"].values[0]):
                temp_dict["abstract"]  = current["abstract"].values[0]
                temp_dict["knowledge_base"] = current["knowledge_base"].values[0]

            # Check if doi is longer
            if temp_dict["doi"] is not None and current["doi"].values[0] is not None and len(temp_dict["doi"]) < len(current["doi"].values[0]):
                temp_dict["doi"] = current["doi"].values[0]
                temp_dict["knowledge_base"] = current["knowledge_base"].values[0]

            # Check if number of citations is greater
            if temp_dict["citations"] is not None and current["citations"].values[0] is not None and int(temp_dict["citations"]) < int(current["citations"].values[0]):
                temp_dict["citations"] = current["citations"].values[0]
                temp_dict["knowledge_base"] = current["knowledge_base"].values[0]

            # Delete the row corresponding to the index from the results dataframe
            result = result[result.id != current["id"].values[0]]
            # result.drop(index=x, inplace = True)
        
        result = result.append(temp_dict, ignore_index=True)

    # Convert Null rows to Python NoneType
    result = result.where((pd.notnull(result)), None)

    # Send final data in result dataframe to a final_publications table that have titles as the primary key.
    if result is not None:
        sql_helper.mysql_connect()
        for index, row in result.iterrows():
            sql = "INSERT IGNORE INTO final_publications (timestamp, title, authors, abstract, knowledge_base, doi, citations) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (row["timestamp"], row["title"], row["authors"], row["abstract"], row["knowledge_base"], row["doi"], row["citations"])
            sql_helper.connection.cursor().execute(sql, val)

            # Connection is not autocommit by default. So you must commit to save your changes.
            sql_helper.connection.commit()
