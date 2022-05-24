#!/usr/bin/env python3
from contextlib import closing
from typing import Iterator

from psycopg2 import extensions

from data_access.types.asset import Asset


def get_assets(connection: extensions.connection, source_type: str) -> Iterator[Asset]:
    """
    Get assets for source_type.

    :param connection: A database connection.
    :param source_type: The type of sensor.
    :return: The assets.
    """
    sql = '''
         select
             asset.asset_uid,
             is_sensor_type.avro_schema_name
         from
             asset, is_asset_assignment, is_asset_definition, is_sensor_type
         where
             asset.asset_uid = is_asset_assignment.asset_uid
         and
             is_asset_assignment.asset_definition_uuid = is_asset_definition.asset_definition_uuid
         and
             is_asset_definition.sensor_type_name = is_sensor_type.sensor_type_name
         and 
             is_sensor_type.avro_schema_name = %s
    '''
    with closing(connection.cursor()) as cursor:
        cursor.execute(sql, [source_type])
        rows = cursor.fetchall()
        for row in rows:
            asset_id = row[0]
            asset_type = row[1]
            yield Asset(id=asset_id, type=asset_type)
