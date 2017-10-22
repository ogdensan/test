#!/usr/bin/python

import MySQLdb
import os
import re
import sys

# Check a valid number of arguments exists
if len(sys.argv) < 6:
    print "Invalid number of arguments."
    exit(1)

scripts_directory = sys.argv[1]
db_user = sys.argv[2]
db_host = sys.argv[3]
db_name = sys.argv[4]
db_pass = sys.argv[5]

db = MySQLdb.connect(host=db_host,
                     user=db_user,
                     passwd=db_pass,
                     db=db_name)

db_cursor = db.cursor()

# Get the current version from database
db_cursor.execute("select version from versionTable")
for row in db_cursor.fetchall():
    current_version = row[0]

# Determine which files to run against the database and save their versions
# Also make sure we only run files with the .sql extension
sql_files = []
versions = []
files = os.listdir(scripts_directory)
for f in files:
    if (
            re.match('(^\d{3}).*.sql', f) and
            int(re.match('(^\d{3}).*.sql', f).group(1)) > int(current_version)
       ):
        sql_files.append(f)
        versions.append(int(re.match('(^\d{3}).*.sql', f).group(1)))

# Check if there are any files to run
if not sql_files:
    print "Database already up to date."
    db.close()
    exit(0)

# Import the sql files
for f in sql_files:
    for line in open("%s/%s" % (scripts_directory, f)):
        print line
        db_cursor.execute(line)

# Update the version
db_cursor.execute("update versionTable set version=%s" % max(versions))
db.commit()
db.close()
