#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shlex
from getpass import getpass

from sys import argv
import signal

from utils import (
  User, InvalidUser, SuperUser, Author, Editor, Reviewer,
  DBParseError, DBConnectError, connect, warn, info, build_database
)


def user_login(user_id: int) -> User:
  """Login user"""

  try:
    conn = connect()
  except (DBParseError, DBConnectError) as err:
    print(err)
    exit(1)

  cursor = conn.cursor()
  user_pass = ""

  def timeout(signum, frame):
    """Timeout handler"""
    print("Password prompt timed out.")
    raise TimeoutError()

  try:
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(5)
    user_pass = getpass("Enter password: ")
    signal.alarm(0)
  except TimeoutError:
    pass

  # get user password and encrypt
  cursor.execute(
    f"""
      SELECT MD5('{user_pass}') AS encrypted_password
    """
  )
  encrypted_password = cursor.fetchone()[0]

  cursor.execute(
    f"""
      SELECT user_type, type_id, password
      FROM credentials
      WHERE user_id = {user_id}
    """
  )
  row = cursor.fetchone()

  # if no record matched, user is nonexistent.
  if row is None:
    warn("User not found")
    return InvalidUser()
  else:
    user_type, type_id, password = row

    # password exists & does not match --> invalid attempt
    if password and password != encrypted_password:
      warn("Incorrect password!\nPlease try again.")
      return InvalidUser()
    elif user_type == "Admin":
      cursor.close()
      return SuperUser(user_id, conn)
    elif user_type == "Author":
      cursor.close()
      return Author(type_id, conn)
    elif user_type == "Editor":
      cursor.close()
      return Editor(type_id, conn)
    elif user_type == "Reviewer":
      cursor.close()
      return Reviewer(type_id, conn)
    else:
      warn("Invalid user type, please contact the system administrator.")
      return InvalidUser()
    

def handle_user_login(request: str) -> User:
  """Handle user login"""
  request_tokens = shlex.split(request)
  if len(request_tokens) == 2:
    user_id = int(request_tokens[1])
    return user_login(user_id)
  else:
    warn("Invalid command: too few or too many arguments")
    return InvalidUser()


def main():
  """Main function"""

  if len(argv) >= 2 and argv[1] == "/rebuild":
    if len(argv) >= 3 and argv[2] == "/populate":
      build_database(load_data=True)
    else:
      build_database()

  user_id = int(input("Enter User ID: "))
  user: User = user_login(user_id)
  while user:
    try:
      request = input(f"{user.prompt} ").strip()
      if request.startswith("login"):
        new_user = handle_user_login(request)
        if new_user:
          user = new_user
      else:
        user.handle_request(request)
    except EOFError:
      warn("Reached end of stream, exiting...")
      break

if __name__ == '__main__':
  main()
