from configparser import ConfigParser
from mysql.connector import MySQLConnection, Error

class DBParseError(Exception):
  """
    Exception raised for errors in reading Database Config.
  """
  pass

class DBConnectError(Exception):
  """
    Exception raised for errors in connecting to Database.
  """
  pass

class ConnectionHandler(MySQLConnection):
  """
    A context manager for MySQLConnection
  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.close()
  
def read_db_config(filename='dbconfig.ini', section='mysql'):
  """
    Read database configuration file and return a dictionary object.
  
    Based on examples from [MySQL with Python tutorial](http://www.mysqltutorial.org/python-mysql)

    Parameters
    ----------
    filename : str
      name of the configuration file
    section : str
      section of database configuration

    Returns
    -------
    dict
      a dictionary of database parameters
  """

  # create parser and read ini configuration file, default 'dbconfig.ini'
  parser = ConfigParser()
  parser.read(filename)
 
  # get section, default to mysql
  dbconfig = {}
  if parser.has_section(section):
    items = parser.items(section)
    for item in items:
      dbconfig[item[0]] = item[1]
  else:
    raise DBParseError('{0} not found in the {1} file'.format(section, filename))
 
  return dbconfig

def connect(filename='dbconfig.ini', section='mysql'):
  """
    Connect to MySQL database.
  """
  db_config = read_db_config(filename)
  conn = ConnectionHandler(**db_config)
  if conn.is_connected():
    return conn
  else:
    raise DBConnectError('connection failed.')
