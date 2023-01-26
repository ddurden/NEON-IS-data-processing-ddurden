#!/usr/bin/env python3
from pathlib import Path
import json
from typing import Callable, Iterator

import geojson
import structlog

from data_access.types.srf import Srf
import data_access.types.geojson_converter as geojson_converter

log = structlog.get_logger()


def load_srfs(out_path: Path, get_srfs: Callable[[str], Iterator[Srf]], group_prefix: str) -> None:
    """
    Write srf loader jsons into the output path.

    :param out_path: The path for writing files, /GROUP/GROUP_science_review_flags.json
    :param get_groups: A function yielding groups.
    :param group_prefix: group_prefix.
    """
    srf_name: str = "_science_review_flags"
    srfs = []
    for srf in get_srfs(group_prefix=group_prefix):
        srfs.append(srf._asdict())
    if not srfs:
        print("Science review is not written")
    else:
        groupname: str = srfs[0]["group_name"]
        srf_file_name: str = groupname + f'{srf_name}.json'
        path: str = Path(out_path, groupname, srf_file_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        srf_data = {}
        srf_data.update({'science_review_flags': srfs})
        json_data = json.dumps(srf_data, indent=4, sort_keys=False, default=str)
        with open(path, 'w') as file:
            file.write(json_data)
        
