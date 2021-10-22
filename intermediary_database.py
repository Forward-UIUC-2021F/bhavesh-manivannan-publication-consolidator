"""
This module stores Open Academic Graph (OAG) publication data on an intermediary MySQL Database.

NOTE: You will need to be connected to the University of Illinois network using a VPN in order to 
connect to the database.
"""
import crawl_OAG
import pandas as pd
import pymysql
import logging
import sshtunnel
from sshtunnel import SSHTunnelForwarder

def oag_to_sql_server(file_path):
  """ Updates the SQL server with latest OAG knowledge base data.

    Args:
        file_path (str): Path to the OAG knowledge base file.

    Returns:
        1 (int): SQL query was successful
       -1 (int): SQL query was not successful

  """
  # Use crawl_helper from crawl_OAG.py to pull data
  publications = crawl_OAG.crawl_helper("", "", file_path)

  for index, row in publications.iterrows():
    citations = row["citations"]
    if citations == "":
      citations = 0

    else:
      citations = int(citations)
    
    connection.ping()  # reconnecting mysql
    with connection.cursor() as cursor:         
        # Create a new record
        sql = "INSERT IGNORE INTO publication_data (title, authors, abstract, doi, citations) VALUES (%s, %s, %s, %s, %s)"
        val = (row["title"], row["authors"], row["abstract"], row["doi"], citations)
        cursor.execute(sql, val)

    # Connection is not autocommit by default. So you must commit to save your changes.
    connection.commit()

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

def test_intermediary_database():
  """Testing suite for intermediary database."""
  open_ssh_tunnel()
  mysql_connect()

  oag_to_sql_server("data\oag_test.txt")
  df = run_query("SELECT * FROM publication_data;")
  assert 'Regulation of K+(86Rb+) absorption by roots of hybrid rice (Weiyou 49) low-salt seedlings.' in df.values
  assert 'S. P. Xie, J. S. Ni' in df.values

  mysql_disconnect()
  close_ssh_tunnel()
  
  print("All intermediary database tests passed.")

test_intermediary_database()