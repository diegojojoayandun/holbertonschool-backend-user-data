#!/usr/bin/env python3

"""
Write a function called filter_datum, returns the log message obfuscated:

- Arguments:
fields: a list of strings representing all fields to obfuscate
redaction: a string representing by what the field will be obfuscated
message: a string representing the log line
separator: a string representing by which character is separating all fields-
in the log line (message).
- The function should use a regex to replace occurrences of certain-
field values.
- filter_datum should be less than 5 lines long and use re.sub to perform-
the substitution with a single regex.
"""

import re
from typing import List

import logging
import os
import mysql.connector

PII_FIELDS = ('name', 'email', 'password', 'ssn', 'phone')


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """constructor"""
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """ filter values in incoming log records using filter_datum """
        return filter_datum(self.fields, self.REDACTION,
                            super(RedactingFormatter, self).format(record),
                            self.SEPARATOR)


def filter_datum(fields: List[str], redaction: str, message: str,
                 separator: str) -> str:
    """returns unclear log messages"""

    for i in fields:
        message = re.sub(i + "=.*?" + separator,
                         i + "=" + redaction + separator,
                         message)
    return message


def get_logger() -> logging.Logger:
    """returns a logger"""
    logger = logging.getLogger('user_data')
    logger.setLevel(logging.INFO)
    logger.propagate = False

    target_handler = logging.StreamHandler()
    target_handler.setLevel(logging.INFO)

    formatter = RedactingFormatter(list(PII_FIELDS))
    target_handler.setFormatter(formatter)

    logger.addHandler(target_handler)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Connect to mysql server with environmental vars
    """
    db_connect = mysql.connector.connect(
        user=os.getenv('PERSONAL_DATA_DB_USERNAME', 'root'),
        password=os.getenv('PERSONAL_DATA_DB_PASSWORD', ''),
        host=os.getenv('PERSONAL_DATA_DB_HOST', 'localhost'),
        database=os.getenv('PERSONAL_DATA_DB_NAME')
    )
    return db_connect


def main() -> None:
    """
    Obtain a database connection using get_db
    and retrieve all rows in the users table and display each row
    """
    db = get_db()
    cur = db.cursor()

    query = ('SELECT * FROM users;')
    cur.execute(query)
    fetch_data = cur.fetchall()

    logger = get_logger()

    for row in fetch_data:
        fields = 'name={}; email={}; phone={}; ssn={}; password={}; ip={}; '\
            'last_login={}; user_agent={};'
        fields = fields.format(row[0], row[1], row[2], row[3],
                               row[4], row[5], row[6], row[7])
        logger.info(fields)

    cur.close()
    db.close()


if __name__ == "__main__":
    main()
