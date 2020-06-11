#!/usr/bin/env python3
from pathlib import Path

from structlog import get_logger

from common.file_crawler import crawl
from common.location_file_parser import LocationFileParser

log = get_logger()


def get_paths(source_path: Path,
              group: str,
              source_type_index: int,
              year_index: int,
              month_index: int,
              day_index: int,
              location_index: int,
              data_type_index: int):
    """
    Link source files into the output directory with the related location group in the path.
    There must be only one location file under the source path.

    :param source_path: The input path.
    :param group: The group to match in the location files.
    :param source_type_index: The input path index of the source type.
    :param year_index: The input path index of the year.
    :param month_index: The input path index of the month.
    :param day_index: The input path index of the day.
    :param location_index: The input path index of the location.
    :param data_type_index: The input path index of the data type.
    """
    paths = []
    group_names = []
    for file_path in crawl(source_path):
        parts = file_path.parts
        source_type = parts[source_type_index]
        year = parts[year_index]
        month = parts[month_index]
        day = parts[day_index]
        location = parts[location_index]
        data_type = parts[data_type_index]
        remainder = parts[data_type_index + 1:]  # everything after the data type
        # put path parts into dictionary
        path_parts = {
            "source_type": source_type,
            "year": year,
            "month": month,
            "day": day,
            "location": location,
            "data_type": data_type,
            "remainder": remainder
        }
        # add the original file path and path parts to paths
        paths.append({"file_path": file_path, "path_parts": path_parts})
        # get the location context group name from the location file
        if data_type == 'location':
            location_file_parser = LocationFileParser(file_path)
            group_names = location_file_parser.matching_context_items(group)
    # location context group name was not found!
    if len(group_names) == 0:
        log.error(f'No location directory found for groups {group_names}.')
    return {'paths': paths, 'group_names': group_names}


def link_paths(paths: list, group_names: list, out_path: Path):
    """
    Loop through the files and link into the output path adding the location
    context group name into the path.

    :param paths: File paths to link.
    :param group_names: Associated location context group names.
    :param out_path: The output path for linking files.
    """
    for path in paths:
        file_path = path.get('file_path')
        parts = path.get('path_parts')
        source_type = parts.get("source_type")
        year = parts.get("year")
        month = parts.get("month")
        day = parts.get("day")
        location = parts.get("location")
        data_type = parts.get("data_type")
        remainder = parts.get("remainder")
        for group_name in group_names:
            link_path = Path(out_path, source_type, year, month, day, group_name, location, data_type, *remainder[0:])
            link_path.parent.mkdir(parents=True, exist_ok=True)
            log.debug(f'file: {file_path} link: {link_path}')
            link_path.symlink_to(file_path)
