#!/usr/bin/env python3
from pathlib import Path
from typing import Callable, Iterator, Set

import geojson
import structlog

from data_access.types.group import Group
import data_access.types.geojson_converter as geojson_converter

log = structlog.get_logger()


def load_groups(out_path: Path, get_group: Callable[[str], Iterator[Group]], group_prefix: str) -> None:
    """
    Write location files into the output path.

    :param out_path: The path for writing files.
    :param get_group: A function yielding groups.
    :param group_prefix: group_prefix.
    """
    for group in get_group(group_prefix=group_prefix):
        group_name = group_prefix[:-1]
#        location_name: str = group.name
        for schema_name in schema_names:
#            path = Path(out_path, group_name, mem_name, f'{mem_name}.json')
            path.parent.mkdir(parents=True, exist_ok=True)
#            geojson_data = geojson_converter.convert_named_location(named_location)
            file_data = geojson.dumps(geojson_data, indent=4, sort_keys=False, default=str)
            with open(path, 'w') as file:
                log.debug(f'writing file: {path}')
                file.write(file_data)   
     
