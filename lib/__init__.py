# lib/config.py
import sqlite3

CONN = sqlite3.connect('company.db', check_same_thread=False)
CURSOR = CONN.cursor()
