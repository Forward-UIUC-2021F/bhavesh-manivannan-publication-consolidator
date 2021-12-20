# publication-consolidator

## Summary

This module aggregates information from scraping tasks and from existing knowledge bases (e.g. MAG, OAG) into a unified database for the EducationToday website.

This module includes the crawlers for the Arxiv, Google Scholar, Springer, and OAG (MAG + Aminer) knowledge bases. Each crawler is in a separate file and can be run by utilizing the crawl(professor, university) function. The consolidator.py file contains a centralized consolidate(professor, university) method which runs all the crawlers to build a single publications dataframe containing all of the publications for the inputted professor that is from the inputted university. Each file also contains unit tests that can be run to verify that nothing broke during potential API or knowledge base updates.

*Note that this module does not handle ranking or keyword assignment related data. It only handles core data: descriptive data of each entity (e.g. research position of an author, number of citations for a publication) and core linking relations between each entity (e.g. current institution of professors).*


## Functional Design 
### Knowledge Base Crawlers:
```
def crawl_oag()/crawl_gscholar()/crawl_arxiv()/crawl_springer():
  ...
   return { 'title': title, 'authors': authors, 'abstract': abstract, 'doi': doi, 'citations': citations }
```
- Input: 
  - Professor name, University name
- Output
  - Pandas dataframe containing knowledgebase data:
      - Arxiv: https://arxiv.org/help/api
      - OAG (MAG + Aminer): https://www.microsoft.com/en-us/research/project/open-academic-graph/
      - Springer: https://dev.springernature.com/ 
                  - https://dev.springernature.com/example-metadata-response 
                  - https://dev.springernature.com/restfuloperations 
      - Google Scholar: https://scholar.google.com/

### Module Storing Latest Version of Microsoft Open Academic Graph on Intermediary SQL Database: 
```
def publication_crawler(file):
  # Crawler helper function that crawls data for publications
  ...

def author_crawler(file):
  # Crawler helper function that crawls data for authors from a file
  ...
```
- Input 
  - File path to the Open Academic Graphic text files.
- Output
  - Updated author_data, publication_data, publication_author SQL tables containing the latest knowledge base data.
- References:
  - https://www.ijstr.org/final-print/oct2015/Query-Optimization-Techniques-Tips-For-Writing-Efficient-And-Faster-Sql-Queries.pdf 

### Distributed Crawler Job Management Module:
```
def crawl(professor, university):
  # Performs scraping tasks from existing knowledge bases. 
  # The queried data is stored in a temporary output_publications SQL table. 
  # It is then consolidated.
  ...
```
- Functional Description
  - Handle each task of searching professors asynchronously through the use of workers.
- Input 
  - Professor name, University name
- Output
  - Scraping information off multiple websites and sources simultaneously using asynchronous workers from Python Celery library. Crawled data sent to output_publications database table. 
- References:
  - https://medium.com/analytics-vidhya/python-celery-distributed-task-queue-demystified-for-beginners-to-professionals-part-1-b27030912fea
  -https://medium.com/analytics-vidhya/python-celery-explained-for-beginners-to-professionals-part-3-workers-pool-and-concurrency-ef0522e89ac5 


### Consolidation Module
```
def consolidate():
    # Handles overlaps and conflicting information from the different knowledge bases. 
    # The final data is uploaded into final_publications table on the database.
    ...
```

- Functional Description
  - Removes duplicate entries in the publication data based on publication titles. 
  - Maximizes the amount of information extracted for a single publication across
  all the knowledge bases.
- Input 
  - output_publications database table
- Output
  - final_publications database table

## Algorithmic Design
Given an input professor and their corresponding university, we first crawl the various knowledge bases for publication data associated with the given professor. The Distributed Crawler module performs all of these crawling tasks simultaneously and stores the output into the output_publications database table. 

Once the publication data is crawled, it is passed into the Consolidation Module where  duplicate publication data is handled. If duplicates exist, the publication information is compiled into a single entry containing the maximum amount of information across the knowledge bases. Then, the final cleaned up publication data is sent to the final_publications database where it is ready to be used by the Forward Education Website.

![image](https://user-images.githubusercontent.com/12843675/137550123-7d1effde-7f13-4d8b-a669-72b8b7a2be9c.png)

