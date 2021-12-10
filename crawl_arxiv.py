"""
This module crawls publication and professor data from the arXiv knowledge base.

Knowledge Base Reference: https://arxiv.org/help/api

Thank you to arXiv for use of its open access interoperability.
"""

import pandas as pd
import json
import arxiv
    
def crawl(professor, university):
    """Crawls Arxiv knowledge base for publications associated with the professor from the specified university.

    Args:
        professor (str): Name of professor
        university (str): Name of university

    Returns:
        publications (pandas dataframe): Data containing the publications' titles, authors, abstracts, and DOI's

    """

    # Initialization
    column_names = ["title", "authors", "abstract", "doi", "citations"]
    publications = pd.DataFrame(columns = column_names)
    first_name = professor.split(" ")[0]
    last_name = ""
    if len(professor.split(" ")) > 1:
        last_name = professor.split(" ")[1]
    
    # API Call to Arxiv API
    search = arxiv.Search(
        query = "au:" + professor,
        max_results = 200,
        sort_by = arxiv.SortCriterion.Relevance
    )

    # Loop through results and find publications matching professor.
    for result in search.results():
        for x in result.authors:
            if first_name in str(x) and last_name in str(x):
                temp_dict = {}
                temp_dict['title'] = result.title
                temp_dict['authors'] = authors_to_string(result.authors)
                temp_dict['abstract'] = result.summary
                temp_dict['doi'] = result.doi
                publications = publications.append(temp_dict, ignore_index=True)
                break
            
    return publications

def ab_name_format(professor):
    """Formats professor name into (First Initial, Middle Initial, Last Name) format.

    Args:
        professor (str): Name of professor

    Returns:
        (str): Professor name in (First Initial, Middle Initial, Last Name) format

    """
    if (professor == ""):
        return ""

    list = professor.split()
    temp = ""

    for i in range(len(list) - 1):
        s = list[i]
          
        # Adds the capital first character 
        temp += (s[0].upper()+'. ')
          
    temp += list[-1].title()
      
    return temp.strip()

def authors_to_string(authors_list):
    """Converts list of Arxiv authors into a comma separated string.

    Args:
        authors_list (list): List of authors from Arxiv.

    Returns:
        temp (str): Comma separated string of all the creators

    """
    temp = ""
    for x in range(len(authors_list)):
        temp += str(authors_list[x])

        if (x != len(authors_list) - 1):
            temp += ", "

    return temp

def test_arxiv():
    """Testing suite for Arxiv crawler"""
    publications = crawl("Pavel Nadolsky", "University of Colorado Boulder")
    assert 'Multiple parton radiation in hadroproduction at lepton-hadron colliders' in publications.values
    assert "10.1063/1.1896698" in publications.values

    publicationsTwo = crawl("Louis Theran", "University of Massachusetts")
    assert "Sparsity-certifying Graph Decompositions" in publicationsTwo.values

    print("All Arxiv Crawler tests passed.")

# test_arxiv()