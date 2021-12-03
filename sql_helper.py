import pandas as pd
import mysql.connector

def mysql_connect():
    """Connect to a MySQL server using the SSH tunnel connection
    
    Returns: 
      connection: Global MySQL database connection
    """
    # Database Credentials
    db_host = '127.0.0.1'
    db_name = "bm12_publications"
    db_user = "bm12"
    db_password = "publications123"
    global connection
    
    connection = mysql.connector.connect(
        host="localhost",
        user=db_user,
        password=db_password,
        db=db_name
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