#!/usr/bin/env python3
from pathlib import Path
import json
from typing import Callable, Iterator

from data_access.threshold import Threshold


def write_file(get_thresholds: Callable[[], Iterator[Threshold]], out_path: Path):
    """
    Write a threshold file into the output path.

    :param get_thresholds: Function yielding threshold objects.
    :param out_path: The path for writing results.
    """
    with open(Path(out_path, 'thresholds.json'), 'w') as file:
        thresholds = []
        for threshold in get_thresholds():
            thresholds.append(threshold._asdict())
        threshold_data = {}
        threshold_data.update({'thresholds': thresholds})
        json_data = json.dumps(threshold_data, indent=4, sort_keys=False, default=str)
        file.write(json_data)
