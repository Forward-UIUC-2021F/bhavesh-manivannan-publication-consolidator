# publication-consolidator

This module aggregates information from scraping tasks and from existing knowledge bases (e.g. MAG, OAG) into a unified database for the EducationToday website.

This module includes the crawlers for the Arxiv, Google Scholar, Springer, and OAG (MAG + Aminer) knowledge bases. Each crawler is in a separate file and can be run by utilizing the crawl(professor, university) function. The consolidator.py file contains a centralized consolidate(professor, university) method which runs all the crawlers to build a single publications dataframe containing all of the publications for the inputted professor that is from the inputted university. Each file also contains unit tests that can be run to verify that nothing broke during potential API or knowledge base updates.

*Note that this module does not handle ranking or keyword assignment related data. It only handles core data: descriptive data of each entity (e.g. research position of an author, number of citations for a publication) and core linking relations between each entity (e.g. current institution of professors).*
