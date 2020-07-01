#!/usr/bin/env python3
from contextlib import closing
from typing import Optional

from cx_Oracle import Connection


def get_named_location_schema_name(connection: Connection, named_location_id: int) -> Optional[str]:
    """
    Return the bound schema name of a named location.

    :param connection: The database connection.
    :param named_location_id: The named location name.
    :return: The schema name.
    """
    sql = '''
        select distinct 
            avro_schema_name
        from 
            is_sensor_type, is_asset_definition, is_asset_assignment, is_asset_location, nam_locn
        where
            is_sensor_type.sensor_type_name = is_asset_definition.sensor_type_name
        and 
            is_asset_definition.asset_definition_uuid = is_asset_assignment.asset_definition_uuid
        and 
            is_asset_assignment.asset_uid = is_asset_location.asset_uid
        and 
            is_asset_location.nam_locn_id = nam_locn.nam_locn_id
        and 
            nam_locn.nam_locn_id = :id
    '''
    with closing(connection.cursor()) as cursor:
        cursor.prepare(sql)
        cursor.execute(None, id=named_location_id)
        row = cursor.fetchone()
        if row is not None:
            return row[0]
    return None
