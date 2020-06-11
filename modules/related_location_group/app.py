#!/usr/bin/env python3
from pathlib import Path

from structlog import get_logger
import environs

import common.log_config as log_config

log = get_logger()


def group_related(data_path: Path,
                  out_path: Path,
                  source_type_index: int,
                  year_index: int,
                  month_index: int,
                  day_index: int,
                  group_index: int,
                  location_index: int,
                  data_type_index: int):
    """
    Link related data and location files into the output path.

    :param data_path: Path for reading files.
    :param out_path: The output path for linking files into.
    :param source_type_index: The input path index of the source type.
    :param year_index: The input path index of the year.
    :param month_index: The input path index of the month.
    :param day_index: The input path index of the day.
    :param group_index: The input path index of the group.
    :param location_index: The input path index of the location.
    :param data_type_index: The input path index of the data type.
    """
    for path in data_path.rglob('*'):
        if path.is_file():
            parts = path.parts
            source_type = parts[source_type_index]
            year = parts[year_index]
            month = parts[month_index]
            day = parts[day_index]
            group = parts[group_index]
            location = parts[location_index]
            data_type = parts[data_type_index]
            remainder = parts[data_type_index + 1:]
            link_path = Path(out_path, year, month, day, group, source_type,
                             location, data_type, *remainder)
            link_path.parent.mkdir(parents=True, exist_ok=True)
            link_path.symlink_to(path)


def main():
    """Group data by related location groups."""
    env = environs.Env()
    data_path = env.path('DATA_PATH')
    out_path = env.path('OUT_PATH')
    log_level = env.log_level('LOG_LEVEL')
    source_type_index = env.int('SOURCE_TYPE_INDEX')
    year_index = env.int('YEAR_INDEX')
    month_index = env.int('MONTH_INDEX')
    day_index = env.int('DAY_INDEX')
    group_index = env.int('GROUP_INDEX')
    location_index = env.int('LOCATION_INDEX')
    data_type_index = env.int('DATA_TYPE_INDEX')
    log_config.configure(log_level)
    log.debug(f'data_path: {data_path} out_path: {out_path}')
    group_related(data_path,
                  out_path,
                  source_type_index,
                  year_index,
                  month_index,
                  day_index,
                  group_index,
                  location_index,
                  data_type_index)


if __name__ == '__main__':
    main()
