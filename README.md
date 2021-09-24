# publication-consolidator

## Summary

This module aggregates information from scraping tasks and from existing knowledge bases (e.g. MAG, OAG) into a unified database for the EducationToday website.

This module includes the crawlers for the Arxiv, Google Scholar, Springer, and OAG (MAG + Aminer) knowledge bases. Each crawler is in a separate file and can be run by utilizing the crawl(professor, university) function. The consolidator.py file contains a centralized consolidate(professor, university) method which runs all the crawlers to build a single publications dataframe containing all of the publications for the inputted professor that is from the inputted university. Each file also contains unit tests that can be run to verify that nothing broke during potential API or knowledge base updates.

*Note that this module does not handle ranking or keyword assignment related data. It only handles core data: descriptive data of each entity (e.g. research position of an author, number of citations for a publication) and core linking relations between each entity (e.g. current institution of professors).*


## Functional Design 
### Knowledge Base Consolidator: 
- Input 
  - Professor name, university
- Output
  - Unified database of scraped information from various knowledge bases:
      - Arxiv: https://www.kaggle.com/Cornell-University/arxiv
      - OAG (MAG + Aminer): https://www.microsoft.com/en-us/research/project/open-academic-graph/
      - Springer: https://dev.springernature.com/ 
                  - https://dev.springernature.com/example-metadata-response 
                  - https://dev.springernature.com/restfuloperations 
   - Google Scholar: https://scholar.google.com/

### Module Storing Latest Version of Static Knowledge Bases on Intermediary SQL Database: 
- Input 
  - Aminer, MAG, Arxiv databases (separate functions for each)
- Output
  - Updated SQL server containing the latest knowledge base data.
- References:
  - https://www.ijstr.org/final-print/oct2015/Query-Optimization-Techniques-Tips-For-Writing-Efficient-And-Faster-Sql-Queries.pdf 

### Distributed Crawler Job Management Module:
- Functional Description
  - Handle each task of searching professors and going through different sources across different machines independently
- Input 
  - List of Crawling Tasks
- Output
  - Scraping information off multiple websites and sources simultaneously. Crawled Data sent to database. 
- References:
  - https://github.com/FS3113/Distributed-System/blob/main/daemon.go 
  - https://iopscience.iop.org/article/10.1088/1755-1315/108/4/042086/pdf

### Distributed Crawler Job Management Module:
- Functional Description
  - Removes duplicate entries in the publication data based on publication titles- Input 
- Input 
  - Pandas dataframe containing Publications data
- Output
  - Pandas dataframe containing Publications data with duplicates removed
- References:
  - Edit distance: https://link.springer.com/chapter/10.1007/978-981-13-0755-3_6 
  - Entity deduplication: https://www.researchgate.net/publication/317177489_Entity_Deduplication_on_ScholarlyData 


