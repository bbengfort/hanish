# hanish.zipcode
# Utility for mapping zip codes to latitude, longitude coords.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon May 08 12:11:01 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: zipcode.py [] benjamin@bengfort.com $

"""
Utility for mapping zip codes to latitude, longitude coords. Loads an
in-memory sqlite database for quickly querying specific zip codes.
"""

##########################################################################
## Imports
##########################################################################

import csv
import sqlite3

from .exceptions import DatabaseError, HanishValueError


SCHEMA = (
    "CREATE TABLE IF NOT EXISTS zipcodes ("
        "zipcode TEXT, "
        "latitude REAL, "
        "longitude REAL"
    ")"
)


##########################################################################
## ZipCodeDB
##########################################################################

class ZipCodeDB(object):
    """
    A ZipCodeDB is loaded from a CSV file that maps US Zip Codes to latitutde,
    longitude coordinates. The data is loaded into an in-memory Sqlite3
    database for quick querying. The data file can be downloaded from:

        https://gist.github.com/erichurst/7882666

    It is also included in the fixtures directory of the repository.

    Usage:

        # Load the db and lookup coordinates
        zipdb = ZipCodeDB.load('fixtures/ziplatlon.csv')
        lat, lon = zipdb.lookup('20001')

        # When done, close the db
        zipdb.close()

    Note: Zip Codes are strings, not numbers (becasuse of leading zeros).
    """

    @classmethod
    def load(klass, path):
        """
        Load the zip code database from a CSV file that has three columns:

            ZIP,LAT,LNG

        If the database is not initialized with load, then it will be empty.
        """

        # Initialize the database and get a cursor
        db = klass()
        cursor = db.conn.cursor()

        # Read the data from the CSV file and insert into db
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                args = (row['ZIP'], float(row['LAT']), float(row['LNG']))
                cursor.execute(
                    "INSERT INTO zipcodes VALUES (?,?,?)", args
                )

        # Commit the database operations
        db.conn.commit()

        # Return the loaded database
        return db

    def __init__(self):
        # Connect to the database
        self.conn = sqlite3.connect(":memory:")

        # Create the table(s) from the schema
        cursor = self.conn.cursor()
        cursor.execute(SCHEMA)
        self.conn.commit()

    def close(self):
        """
        Close the connection to the database, removing data from memory and
        allowing no further accesses (otherwise an exception will be raised).
        """
        self.conn.close()
        self.conn = None

    def execute(self, sql, *args, **kwargs):
        """
        Helper function that creates a cursor and executes a single SQL
        statement, returning the cursor to read the results of the query.
        """
        # Check the connection
        if self.conn is None:
            raise DatabaseError(
                "Zip Code database has been closed and removed from memory"
            )

        # Execute the query and return
        cursor = self.conn.cursor()
        cursor.execute(sql, *args, **kwargs)
        return cursor


    def lookup(self, zipcode):
        """
        Lookup the geographic coordinates for a given U.S. postal code. If the
        postal code is not in the database, this method raises a ValueError.

        Parameters
        ----------
        zipcode: string
            A United States 5-digit postal code

        Returns
        -------
        latitude: float
            The latitude portion of the geo-coordinates for the zip code

        longitude: float
            The longitude portion of the geo-coordinates for the zip code
        """

        # Execute the query
        cursor = self.execute(
            "SELECT latitude, longitude FROM zipcodes WHERE zipcode=?", (zipcode,)
        )

        # Fetch, validate, and return the value
        value = cursor.fetchone()
        if value is None:
            raise HanishValueError(
                "could not find zipcode '{}'".format(zipcode)
            )

        return value

    def count(self):
        """
        Returns the number of zipcodes that are currently in the database.
        """
        # Execute the query
        cursor = self.execute(
            "SELECT count(zipcode) FROM zipcodes"
        )

        # Fetch, validate and return the value
        return cursor.fetchone()[0]
