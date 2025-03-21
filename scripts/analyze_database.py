import sys
import os
import json
from dotenv import load_dotenv
import requests
import time

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#from app import db
from app.app import db, create_app
from app.models import Vendor
import requests
import sqlite3
 
def connect_to_db():
    """Connect to the SQLite database."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'instance', 'vendors.db')
    connection = sqlite3.connect(db_path)

    print("Connection established.")
    return connection

def check_for_duplicates(connection):
    """Check for duplicate entries in the vendors table."""
    cursor = connection.cursor()
    query = """
    SELECT name, address, COUNT(*)
    FROM vendors
    GROUP BY name, address
    HAVING COUNT(*) > 1
    """
    cursor.execute(query)
    duplicates = cursor.fetchall()

    print('\n')
    #print('Duplicate entries:')
    print('no of duplicates:', len(duplicates))
    # for duplicate in duplicates:
    #     print(duplicate)
    return duplicates

def count_total_entries(connection):
    """Count the total number of entries in the vendors table."""
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM vendors"
    cursor.execute(query)
    total_entries = cursor.fetchone()[0]

    print(f"Total entries in the vendors table: {total_entries}")
    return total_entries

def delete_duplicates(connection, duplicates):
    """Delete duplicate entries from the vendors table."""
    cursor = connection.cursor()
    for duplicate in duplicates:
        name, address, count = duplicate
        # Keep one entry and delete the rest
        query = """
        DELETE FROM vendors
        WHERE rowid NOT IN (
            SELECT rowid
            FROM vendors
            WHERE name = ? AND address = ?
            LIMIT 1
        )
        AND name = ? AND address = ?
        """
        cursor.execute(query, (name, address, name, address))
    connection.commit()
    print("Duplicate entries deleted.")

    return  

def save_db_to_csv(connection):
    """Save the vendors table to a CSV file."""

    cursor = connection.cursor()
    query = "SELECT * FROM vendors"
    cursor.execute(query)

    with open('vendors.csv', 'w') as f:
        for row in cursor.fetchall():
            f.write(','.join(map(str, row)) + '\n')

    print("Database saved to vendors.csv.")
    return

def close_connection(connection):

    connection.close()
    print("Connection closed.")
    return

def main():

    connection = connect_to_db() # Connect to the SQLite database
    total_entries = count_total_entries(connection) # Count total entries in the vendors table
    duplicates = check_for_duplicates(connection) # Check for duplicate entries

    print('Do you want to delete the duplicates?')
    print('Enter y/n')
    response = input()
    if response.lower() == 'y':
        delete_duplicates(connection, duplicates) # Delete duplicate entries
        total_entries = count_total_entries(connection) # Count total entries in the vendors table
    else:
        print('No duplicates were deleted.')
    
    #save_db_to_csv(connection) # Save the vendors table to a CSV file
    close_connection(connection) # close connection
    return

if __name__ == "__main__":
    '''main function'''
    main()