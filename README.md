# CS 61: Database Systems
## MySQL Application
## Fall 2022
## Project by: [Ke Lou](https://github.com/fpoon777), [Amittai Siavava](https://github.com/siavava)

To test our program, run `make`. Alternatively, run `main.py`.

See [requirements.txt][reqs] for Python dependencies.



> **Note**
> 1. Like any logical program, functionality is heavily dependent on
>    the underlying database being properly built.
>    For this:
>    - Modify [dbconfig.ini][dbconfig] to point to either a local or remote MySQL database. Or use ours.
>    - If running on a new database, provide the `/rebuild` flag to reconstruct the table structure.
>       - Additionally, provide the `/populate` flag to populate the database with sample data. Otherwise, the database will be empty, with only two admin users available to register others.
> 2. Please only specify your user ID at the initial prompt.
>      - Do not add the `login` command.
>      - Thereafter, switching users will follow the usual `login <user-id>` command.

---

## Note on Passwords

Passwords are handled leniently. They are not required
(just press enter in the password prompt when registering a new user).
however, if a password is provided, it must be matched exactly
when logging in.

The two default users are:
- `Admin 1` with password `siavava`
- `Admin 2` with password `lou`

If modifications are desired, see the end of [tables.sql][tables]

---

## Note on Database Structure

See the [sql folder][sql] for relevant SQL code for creating, managing, and 
populating the database.

See [dbutils][dbutils] for some Python code that interacts with the database.

Other modules ([Author][author], [Editor][editor], [Reviewer][reviewer], etc.)
interact briefly with the database to perform their respective tasks.

---

Here's the composition of this directory:

```bash

# files in the directory
λ> tree
.
├── Makefile
├── README.md
├── assignment.md
├── dbconfig.ini
├── main.py
├── requirements.txt
└── utils
    ├── __init__.py
    ├── author.py
    ├── dbconfig.py
    ├── dbutils.py
    ├── editor.py
    ├── logging.py
    ├── reviewer.py
    ├── sql
    │   ├── Makefile
    │   ├── README.md
    │   ├── assignment.md
    │   ├── clear.sql
    │   ├── data.sql
    │   ├── procedures.sql
    │   ├── procedurestest.sql
    │   ├── tables.sql
    │   ├── triggers.sql
    │   ├── triggertest.sql
    │   └── views.sql
    ├── superuser.py
    └── user.py

2 directories, 26 files


# file composition
λ> cloc .                          
      28 text files.
      26 unique files.                              
      13 files ignored.

github.com/AlDanial/cloc v 1.94  T=0.07 s (390.1 files/s, 66834.6 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
SQL                              8            140            190           1616
Python                          10            341            589           1145
Markdown                         3             81              0            215
Text                             1              0              0             70
make                             2             14             13             30
JSON                             1              0              0              6
INI                              1              0              0              5
-------------------------------------------------------------------------------
SUM:                            26            576            792           3087
-------------------------------------------------------------------------------
```

---

## Example Run

```bash
λ> ./main.py /rebuild /withdata
Database built successfully
Inserting data into database...
Data inserted successfully
Enter User ID: 7
Enter password: 
Hello, Drake Leach 

Status:
----------------------------------------------------

Last Change: 2024-06-24

----------------------------------------------------
| Manuscript #### |                         Status |
----------------------------------------------------
| Manuscript    3 |                       accepted |
----------------------------------------------------
| Manuscript   37 |                 in typesetting |
----------------------------------------------------
| Manuscript   74 |                          ready |
----------------------------------------------------
| Manuscript  148 |                          ready |
----------------------------------------------------


Author 5>  {do more interesting stuff here}
```

![screenshot][screenshot]




[dbconfig]: dbconfig.ini
[tables]: utils/sql/tables.sql
[reqs]: requirements.txt
[sql]: utils/sql
[dbutils]: utils/dbutils.py
[author]: utils/author.py
[editor]: utils/editor.py
[reviewer]: utils/reviewer.py
[screenshot]: screenshot.png
