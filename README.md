# publication-consolidator

## Summary

This module aggregates information from scraping tasks and from existing knowledge bases (e.g. MAG, OAG) into a unified database for the EducationToday website.

This module includes the crawlers for the Arxiv, Google Scholar, Springer, and OAG (MAG + Aminer) knowledge bases. Each crawler is in a separate file and can be run by utilizing the crawl(professor, university) function. The consolidator.py file contains a centralized consolidate(professor, university) method which runs all the crawlers to build a single publications dataframe containing all of the publications for the inputted professor that is from the inputted university. Each file also contains unit tests that can be run to verify that nothing broke during potential API or knowledge base updates.

*Note that this module does not handle ranking or keyword assignment related data. It only handles core data: descriptive data of each entity (e.g. research position of an author, number of citations for a publication) and core linking relations between each entity (e.g. current institution of professors).*


## Setup

List the steps needed to install your module's dependencies: 

1. Install the necessary Python dependencies:
```
pip install -r requirements.txt 
```

2. Create a MySQL server and update the server credentials in sql_helper.py. Information on how to install and setup a MySQL server can be found here: https://dev.mysql.com/doc/refman/8.0/en/installing.html 

3. Run the SQL CREATE statements located in the sql_tables/ directory. This will create the necessary tables for the publication-consolidator module. 

4. Download the Open Academic Graph papers and authors files from https://www.microsoft.com/en-us/research/project/open-academic-graph/ and store the .txt files in the data/ directory. Then run the intermediary_database.py store_publications() and store_authors() on each file like below: 
```
intermediary_database.store_publications()("data/mag_papers_0.txt")
intermediary_database.store_authors()("data/mag_authors_0.txt")
```

5. Install and Configure Redis. Information on how to do this on Ubuntu 18.04 can be found here: https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04 

6. Make sure to have Redis server running on a port that is free. If the default :6379 port is taken, you will need to refactor the Redis files by replacing :6379 with your preferred port. Then you will need to run "make" in order to compile the updated Redis files. You can check to see if your Redis Server is running with the following command:
```
sudo netstat -lnp | grep redis
```

7. Now that the Redis server is running, you are able to run the Celery task located in tasks.py. Make sure to update the BROKER_URL with the correct port that your Redis server is running on. The Celery task can be started with the following command:
```
celery -A tasks worker --pool=gevent --concurrency=3 --loglevel=info
```
Note: The concurrency flag needs to be changed if you add or remove crawling tasks. Currently, the only functioning crawling tasks are crawl_arxiv, crawl_OAG, and crawl_springer and that is why the number is set to 3.

8. Once Celery is successfully running on the Redis server, the distributed_crawler.py can be run simply with:

```
python3 distributed_crawler.py
```

9. The updated MySQL database can be viewed using tools such as MySQL Workbench.

***Repo File Structure:***
```
publication-consolidator/
    - requirements.txt
    - data/ 
        -- oag_test.txt
        -- oag_authors.txt
    - sql_tables/
        -- author_data.sql
        -- final_publications.sql
        -- output_publications.sql
        -- publication_author.sql
        -- publication_data.sql
    - consolidator.py
    - crawl_arxiv.py
    - crawl_gscholar.py
    - crawl_OAG.py
    - crawl_springer.py
    - distributed_crawler.py
    - intermediary_database.py
    - sql_helper.py
    - tasks.py
```

***Descriptions of important files:***
* `data/`: Directory to store OAG .txt files
* `sql_tables/`: Contains the SQL CREATE statements for each MySQL database table
* `consolidator.py`: Handles overlaps and conflicting information from the different knowledge bases
* `crawl_arxiv.py`: Crawls publication and professor data from the arXiv knowledge base
* `crawl_gscholar.py`: Crawls publication and professor data from the Google Scholar knowledge base
* `crawl_OAG.py`: Crawls publication and professor data from the Microsoft Open Academic Graph knowledge base
* `crawl_springer.py`: Crawls publication and professor data from the Springer knowledge base.
* `distributed_crawler.py`: Distributed Crawler Management Module that performs scraping tasks from 
existing knowledge bases (e.g. OAG, Springer, Arxiv, etc.) asynchronously through the use of workers and stores data 
into a unified database
* `intermediary_database.py`: This program extracts professor and publication data from Microsoft Open Academic Graph (OAG) Knowledge Base files
* `sql_helper.py`: This file contains helper functions for connecting to MySQL servers and running queries
* `tasks.py`: Contains the crawl_task() function that will be run asynchronously

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
def store_publications(file):
  # Crawler helper function that crawls data for publications
  ...

def store_authors(file):
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
  - https://medium.com/analytics-vidhya/python-celery-explained-for-beginners-to-professionals-part-3-workers-pool-and-concurrency-ef0522e89ac5 


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


## Demo video
Make sure to include a video showing your module in action and how to use it in this section. Github Pages doesn't support this so I am unable to do this here. However, this can be done in your README.md files of your own repo. Follow instructions [here](https://stackoverflow.com/questions/4279611/how-to-embed-a-video-into-github-readme-md) of the accepted answer 

## Algorithmic Design
Given an input professor and their corresponding university, we first crawl the various knowledge bases for publication data associated with the given professor. The Distributed Crawler module performs all of these crawling tasks simultaneously and stores the output into the output_publications database table. 

Once the publication data is crawled, it is passed into the Consolidation Module where  duplicate publication data is handled. If duplicates exist, the publication information is compiled into a single entry containing the maximum amount of information across the knowledge bases. Then, the final cleaned up publication data is sent to the final_publications database where it is ready to be used by the Forward Education Website.

![image](https://user-images.githubusercontent.com/12843675/137550123-7d1effde-7f13-4d8b-a669-72b8b7a2be9c.png)


## Issues and Future Work
* Fix the Google Scholar Crawler by creating a reverse proxy to avoid being flagged as malicious activity by Google.
* Optimize SQL queries to pull from the large OAG database tables.
* Handle edge cases in the crawl_OAG.py file such as middle initials of professors.

## References: 
* Arxiv: https://arxiv.org/help/api
* OAG (MAG + Aminer): https://www.microsoft.com/en-us/research/project/open-academic-graph/
* Springer: https://dev.springernature.com/ 
* Google Scholar: https://scholar.google.com/
* Distributed Task Queue using Celery: 
  - https://medium.com/analytics-vidhya/python-celery-distributed-task-queue-demystified-for-beginners-to-professionals-part-1-b27030912fea 
  - https://medium.com/analytics-vidhya/python-celery-explained-for-beginners-to-professionals-part-3-workers-pool-and-concurrency-ef0522e89ac5 
* Redis Installation on Ubuntu: https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04 