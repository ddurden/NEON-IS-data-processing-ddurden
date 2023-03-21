"""Module to read data product keywords from the database."""
from contextlib import closing
from typing import List

from data_access.db_connector import DbConnector


def get_keywords(connector: DbConnector, data_product_id: str) -> List[str]:
    """
    Get the data product keywords for the given ID.

    :param connector: A database connection.
    :param data_product_id: The data product ID.
    :return: The data product keywords.
    """
    connection = connector.get_connection()
    schema = connector.get_schema()
    sql = f'''
        select 
            keyword.word 
        from 
            {schema}.keyword, {schema}.dp_keyword
        where
            dp_keyword.dp_idq = %s
        and 
            dp_keyword.keyword_id = keyword.keyword_id
    '''
    keywords = []
    with closing(connection.cursor()) as cursor:
        cursor.execute(sql, [data_product_id])
        rows = cursor.fetchall()
        for row in rows:
            keyword = row[0]
            keywords.append(keyword)
    return keywords
