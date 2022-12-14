#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mysql.connector import MySQLConnection, Error, errorcode, FieldType
from getpass import getpass
from datetime import date
import shlex
from .dbconfig import read_db_config
from .user import User
from .logging import Logging, warn

# Author Functionalities
class Author(User):
  def __init__(self, author_id: int, conn: MySQLConnection):
    self.author_id = author_id
    self.conn = conn
    self.is_valid = self.login()

  def __bool__(self):
    return self.is_valid

  @property
  def prompt(self):
    """
      Get the user prompt for the terminal
    """
    return f"Author {self.author_id}> "


  # 3. author login.
  def login(self):
    """
      Author login.
      
      Params
      ------
      `author_id`: int
        Author ID.

      Returns
      -------
      bool: True if the author was logged in successfully, False otherwise.
    """

    query = f"""
      SELECT CONCAT('Hello, ', Author.f_name, ' ', Author.l_name)
      FROM Author WHERE Author.author_ID = {self.author_id}"""

    success = False

    try:
      cursor = self.conn.cursor()
      cursor.execute(query)
      result = cursor.fetchone()
      cursor.close()
      if result:
        success = True
        print(result[0], "\n")
        print(f"Status:\n{self.status()}\n")
    except Error as error:
      print(error)

    return success

  # 2. author status.
  def status(self):
    """
      Return a status of the current author's manuscripts.

      Parameters
      ----------
      `author_id`: int
        Author ID.

      Returns
      -------
        String value representing the status of all manuscripts
        where author is primary author.
    """
    query = f"""
      SELECT LeadAuthorManuscripts.manuscript_number, Manuscript.status
      FROM LeadAuthorManuscripts, Manuscript
      WHERE LeadAuthorManuscripts.author_id = {self.author_id}
      AND LeadAuthorManuscripts.manuscript_number = Manuscript.manuscript_number
    """

    time_stamp = f"""
      SELECT MAX(Manuscript.status_change_date)
      FROM Manuscript, LeadAuthorManuscripts
      WHERE LeadAuthorManuscripts.author_id = {self.author_id}
      AND LeadAuthorManuscripts.manuscript_number = Manuscript.manuscript_number
    """

    cursor = self.conn.cursor()
    cursor.execute(query)
    
    title = "Status"
    title = f"| Manuscript #### | {title:>30} |"
    delim = "-" * len(title)

    results = ""
    for row in cursor:
      manuscript_number, status = row
      results += f"| Manuscript {manuscript_number:4d} | {status:>30} |\n{delim}\n"
    if len(results) == 0:
      results = "Author has no manuscripts."
    else:
      cursor.execute(time_stamp)
      last_change_date = cursor.fetchone()[0]
      title = f"\nLast Change: {last_change_date}\n\n{delim}\n" + title
      results = f"{delim}\n{title}\n{delim}\n{results}"
    cursor.close()

    return Logging.info(results)

    
  # 4. author submit
  def submit_manuscript(self, title: str, affiliation: str, i_code: str,
    author_two="", author_three="", author_four="", filename="unspecified"):
    """
      Submit a manuscript.

      Parameters
      ----------
      `title`: str
        Title of the manuscript.
      `affiliation`: str
        Affiliation (organization) of the author.
      `i_code`: str
        Institutional code of the author.
      `author_two`: int
        Author ID of the second author.
      `author_three`: int
        Author ID of the third author.
      `filename`: str
        Filename of the manuscript.

      Returns
      -------
      bool: True if the manuscript was submitted successfully, False otherwise.
    """
    author_one = self.author_id

    queries = [
      f"""
        INSERT INTO Manuscript (title, date_received, status, RICodes_code)
        VALUES ('{title}', \"{date.today()}\", "submitted", '{i_code}')
      """,
      f"""
        INSERT INTO Manuscript_Author (Author_author_id, Manuscript_manuscript_number, author_ordinal)
        VALUES ({author_one}, (SELECT MAX(manuscript_number) FROM Manuscript), 1)
      """
    ]

    if author_two:
      author_two_tokens = author_two.split(" ")
      author_two_fname = author_two_tokens[0]
      author_two_lname = author_two_tokens[1] if len(author_two_tokens) > 1 else ""
      print(f"Author two is:  --> {author_two_fname}, {author_two_lname}")
      self.register_author_if_nonexistent(author_two_fname, author_two_lname, "", affiliation)
      author_two_id = self.get_author_id(author_two_fname, author_two_lname)
      queries.append(f"""
        INSERT INTO Manuscript_Author (Author_author_id, Manuscript_manuscript_number, author_ordinal)
        VALUES ({author_two_id}, (SELECT MAX(manuscript_number) FROM Manuscript), 2)
      """)
    if author_three:
      author_three_tokens = author_three.split(" ")
      author_three_fname = author_three_tokens[0]
      author_three_lname = author_three_tokens[1] if len(author_three_tokens) > 1 else ""
      self.register_author_if_nonexistent(author_three_fname, author_three_lname, "", affiliation)
      author_three_id = self.get_author_id(author_three_fname, author_three_lname)
      queries.append(f"""
        INSERT INTO Manuscript_Author (Author_author_id, Manuscript_manuscript_number, author_ordinal)
        VALUES ({author_three_id}, (SELECT MAX(manuscript_number) FROM Manuscript), 3)
      """)

    if author_four:
      author_four_tokens = author_four.split(" ")
      author_four_fname = author_four_tokens[0]
      author_four_lname = author_four_tokens[1] if len(author_four_tokens) > 1 else ""
      self.register_author_if_nonexistent(author_four_fname, author_four_lname, "", affiliation)
      author_four_id = self.get_author_id(author_four_fname, author_four_lname)
      queries.append(f"""
        INSERT INTO Manuscript_Author (Author_author_id, Manuscript_manuscript_number, author_ordinal)
        VALUES ({author_four_id}, (SELECT MAX(manuscript_number) FROM Manuscript), 4)
      """)

    success = False

    try:
      cursor = self.conn.cursor()
      for query in queries:
        cursor.execute(query)
        self.conn.commit()
      success = True
    except Error as error:
      print(error)
    finally:
      cursor.close()

    return success

  def get_author_id(self, fname: str, lname: str):
    """
      Get the author ID of an author.

      Parameters
      ----------
      `fname`: str
        First name of the author.
      `lname`: str
        Last name of the author.

      Returns
      -------
      int: Author ID.
    """
    query = f"""
      SELECT author_id FROM Author
      WHERE f_name = '{fname}'
      AND l_name = '{lname}'
    """

    cursor = self.conn.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    return int(row[0])


  # 1. Register a new author.
  def register_author(self, f_name: str, l_name: str, email: str, affiliation: str):
    """
      Register a new author.
      
      Params
      ------
      `f_name`: str
        First name of the author.
      `l_name`: str
        Last name of the author.
      `email`: str
        Email of the author.
      `affiliation`: str
        Affiliation (organization) of the author.

      Returns
      -------
      bool: True if the author was registered successfully, False otherwise.
    """


    query = f"""
      INSERT INTO Author (f_name, l_name, email, Affiliation_affiliation_ID)
      VALUES ('{f_name}', '{l_name}', '{email}', '{affiliation}')
    """

    password = getpass("Enter password: ")
    
    password_query = f"""
      UPDATE credentials
      SET password = MD5('{password}')
      WHERE
        user_type = "Author"
        AND type_id = (SELECT author_ID FROM Author WHERE f_name = '{f_name}' AND l_name = '{l_name}')
    """

    success = False

    try:
      cursor = self.conn.cursor()
      cursor.execute(query)
      self.conn.commit()
      if password:
        cursor.execute(password_query)
        self.conn.commit()
      author_id = cursor.lastrowid
      success = True
      user_id_query = f"""
        SELECT user_id from credentials
        WHERE user_type = 'Author'
        AND type_id = {author_id}"""
      cursor.execute(user_id_query)
      user_id = int(cursor.fetchone()[0]) # get the user_id from the credentials table
      print(f"Registered User ID: {user_id}") # print the user_id for the author

    except Error as error:
      print(error)
    finally:
      cursor.close()

    return success

  def register_author_if_nonexistent(self, f_name: str, l_name: str, email: str, affiliation: str):
    """
      Register a new author if the author does not exist.

      Params
      ------
      `f_name`: str
        First name of the author.
      `l_name`: str
        Last name of the author.
      `email`: str
        Email of the author.
      `affiliation`: str
        Affiliation (organization) of the author.

      Returns
      -------
      bool: True if the author was registered successfully, False otherwise.
    """

    query = f"""
      SELECT * FROM Author
      WHERE f_name = '{f_name}'
      AND l_name = '{l_name}'
    """

    cursor = self.conn.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    if row:
      return False
    else:
      return self.register_author(f_name, l_name, email, affiliation)

  def handle_request(self, request: str):
    """
      Handle a request

      Parameters
      ----------
      `request`: str
        The request to handle.
        Possible values:

        - `register author <fname> <lname> <email> <affiliation>`
        - `login <id>`
        - `submit <title> <Affiliation> <ICode> <author2> <author3> <author4> <filename>`
        - `status`
    """

    request_tokens  = shlex.split(request)
    request_type = request_tokens[0].lower() if len(request_tokens) > 0 else ""

    if request_type == "status":
      print(f"Author ID: {self.author_id}\n{self.status()}")

    elif request_type == "register":
      if len(request_tokens) < 6:
        print("Invalid request: too few arguments.")
        return
      if request_tokens[1].lower() != "author":
        print("Invalid request.")
        return

      f_name = request_tokens[2]
      l_name = request_tokens[3]
      email = request_tokens[4]
      affiliation = request_tokens[5]

      if self.register_author_if_nonexistent(f_name, l_name, email, affiliation):
        print("Author registered successfully.")
      else:
        print("Author registration failed.")
    elif request_type == "submit":
      if len(request_tokens) < 4:
        print("Invalid request: not enough arguments.")
        return

      title = request_tokens[1]
      affiliation = request_tokens[2]
      i_code = request_tokens[3]
      
      author_two = request_tokens[4] if len(request_tokens) > 4 else ""
      author_three = request_tokens[5] if len(request_tokens) > 5 else ""
      author_four = request_tokens[6] if len(request_tokens) > 6 else ""
      filename = request_tokens[7] if len(request_tokens) > 7 else ""
      

      if self.submit_manuscript(title, affiliation, i_code, author_two, author_three, author_four, filename):
        print("Manuscript submitted successfully.")
      else:
        print("Manuscript submission failed.")

    else:
      print("Invalid request.")
    

def test_author():
  # the mysql self.connection instance.

  db_config = read_db_config()
  conn = MySQLConnection(**db_config)

  for _ in range(3):
    print("\n\nTesting author instantiation, login, and status...\n")
    author_id = int(input("Enter author ID: "))
    author = Author(author_id, conn)
    if author:
      print("Author logged in successfully.")
    else:
      print("Author login failed.")
      continue

    print("\n\nTesting author registration...\n")
    f_name = input("First name: ")
    l_name = input("Last name: ")
    email = input("Email: ")
    affiliation = input("Affiliation: ")

    print("Before registration:")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Author")
    for row in cursor:
      print(row)
    cursor.close()

    success = author.register_author_if_nonexistent(f_name, l_name, email, affiliation)

    if success:
      print("Author registered successfully.")
      print("After registration:")
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM Author")
      for row in cursor:
        print(row)
      cursor.close()

    else:
      print("Author registration failed.")

    print("\n\nTesting submission of manuscripts...\n")
    title = input("Title: ")
    affiliation = input("Affiliation ID: ")
    icode = input("i-code: ")
    author_two = input("Author two: ") or None
    author_three = input("Author three: ") or None
    author_four = input("Author four: ") or None
    print(f"Current status: \n{author.status()}")
    success = author.submit_manuscript(title, affiliation, icode, author_two, author_three, author_four)
    if success:
      print("Manuscript submitted successfully.")
      print(f"New status: {author.status()}")
    else:
      print("Manuscript submission failed.")

    print(f"Author status: \n{author.status()}")

def test_author_handle_request():
  print("\n\nTesting author handle request...\n")
  author_id = int(input("Enter author ID: "))
  author = Author(author_id)
  if author:
    print("Author logged in successfully.")
  else:
    print("Author login failed.")
    return

  while True:
    request = input("Enter request: ")
    author.handle_request(request)
    print(f"Author status: \n{author.status()}")
  return

if __name__ == "__main__":
  test_author()
  test_author_handle_request()
  print("Done.")
