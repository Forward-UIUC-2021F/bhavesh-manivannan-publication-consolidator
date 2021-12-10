from tasks import crawl_task
professor = "Jiawei Han"
university = "University of Illinois Urbana-Champaign"

# Arxiv Task
result = crawl_task.delay("crawl_arxiv", professor, university)
print(result)

# Springer Task
springer = crawl_task.apply_async(args=["crawl_springer", professor, university])
print(springer)

# OAG Task
oag = crawl_task.apply_async(args=["crawl_oag", professor, university])
print(oag)

# GScholar Task
# gscholar = crawl_task.apply_async(args=["crawl_gscholar", professor, university])
# print(gscholar)