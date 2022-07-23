#!/usr/bin/python

import sqlite3

conn = sqlite3.connect("db.sqlite3")
print("Opened database successfully")

conn.execute(
    """CREATE TABLE ACTIVE_UPLOADS
         (ID            INTEGER PRIMARY KEY     AUTOINCREMENT,
         FILESIZE       BIGINT     NOT NULL,
         UUID           TEXT     NOT NULL);"""
)
print("Table ACTIVE_UPLOADS created successfully")

conn.execute(
    """CREATE TABLE VIDEO_INDEX
         (ID            INTEGER PRIMARY KEY     AUTOINCREMENT,
         IDENTIFIER     TEXT     NOT NULL,
         PATH           TEXT     NOT NULL,
         TIMESTAMP      INTEGER  NOT NULL
         );"""
)
print("Table VIDEO_INDEX created successfully")

conn.close()
