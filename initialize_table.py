import pymysql
import pandas as pd
import logging
import sshtunnel
from sshtunnel import SSHTunnelForwarder

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
    tunnel.close()

""""
mydb = mysql.connector.connect(
	host="owl2.cs.illinois.edu",
	user="juefeic2",
	password="0202141208",
	database="juefeic2_educationtoday"
)

mycursor = mydb.cursor()

# column priority can be used to prioritize tasks,
# then the master server can assign tasks follow this priority
mycursor.execute("DROP TABLE IF EXISTS Tasks")
mycursor.execute("CREATE TABLE Tasks (task VARCHAR(20), priority int)")

sql = 'insert into Tasks (task, priority) values (%s, %s)'
for i in range(1000):
	mycursor.execute(sql, ('{} plus {}'.format(i, i), i))

mycursor.execute('drop table if exists Output')
mycursor.execute("CREATE TABLE Output (task varchar(20), result varchar(20), timestamp varchar(100), status varchar(100))")


"""

open_ssh_tunnel()
mysql_connect()

connection.ping()
with connection.cursor() as cursor:
	cursor.execute("DROP TABLE IF EXISTS Tasks")
	cursor.execute("CREATE TABLE Tasks (task VARCHAR(20), priority int)")
	connection.commit()
	
for i in range(1000):
	connection.ping()
	with connection.cursor() as cursor:
		sql = 'insert into Tasks (task, priority) values (%s, %s)'
		cursor.execute(sql, ('{} plus {}'.format(i, i), i))
connection.commit()
connection.ping()

with connection.cursor() as cursor:
	cursor.execute('drop table if exists Output')
	cursor.execute("CREATE TABLE Output (task varchar(20), result varchar(20), timestamp varchar(100), status varchar(100))")
connection.commit()

mysql_disconnect()
close_ssh_tunnel()