#!/usr/bin/env python3
from contextlib import closing
from typing import List

from psycopg2 import extensions

from data_access.types.active_period import ActivePeriod
from data_access.types.property import Property
from data_access.get_named_location_active_periods import get_active_periods

def get_groups(connection: extensions.connection, group_prefix: str) -> List[str]:
    """
    Get groups for a group prefix, i.e., pressure-air_.

    :param connection: A database connection.
    :param group_prefix: A group prefix.
    :return: The groups.
    """
    sql = '''
        select
             g2.group_id, g2.group_name
        from 
             "group" g2 
        where
            g2.group_id in (select gm.member_group_id 
        from 
            "group" g, group_member gm
        where
          	g.group_id = gm.group_id 
        and
            g.group_name like '%s%%')
    '''
     name = group_prefix[:-1]
     with closing(connection.cursor()) as cursor:
        cursor.execute(sql, group_prefix)
        rows = cursor.fetchall()
        for row in rows:
            mem_id = row[0]
            mem_name = row[1]
            active_periods: List[ActivePeriod] = get_group_active_periods(connection, group_id=mem_id)
            properties: List[Property] = get_group_properties(connection, group_id=mem_id)
            group_name: List[str] = get_group_names(connection, group_prefix=group_prefix)
            groups = Group(name=mem_name, group=group_name, active_periods=active_periods, properties=properties)
            yield groups
  
