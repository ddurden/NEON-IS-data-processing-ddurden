import os
import pathlib

from structlog import get_logger
import environs

import lib.file_linker as file_linker
import lib.file_crawler as file_crawler
import lib.location_file_context as location_file_context
import lib.log_config as log_config

log = get_logger()


def process(source_path, group, out_path):
    """
    Link source files into the output directory with the related location group in the path.
    There must be only one location file under the source path.
    :param source_path: The input path.
    :param group: The group to match in the location files.
    :param out_path: The output path.
    """
    paths = []
    group_name = None
    for file_path in file_crawler.crawl(source_path):
        # parse path elements
        parts = pathlib.Path(file_path).parts
        source_type = parts[3]
        year = parts[4]
        month = parts[5]
        day = parts[6]
        location = parts[7]
        data_type = parts[8]
        remainder = parts[9:]  # everything after the data type
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
        # add the original file path and the path parts to the path list
        paths.append({"file_path": file_path, "path_parts": path_parts})

        # get the location context group name from the location file
        if data_type == 'location':
            group_name = location_file_context.get_matching_item(file_path, group)

    # location context group name was not found!
    if group_name is None:
        log.error('No location directory found.')
    # context group name found, link all the files into the output directory
    else:
        link(paths, group_name, out_path)


def link(paths, group_name, out_path):
    """
    Loop through the files and link into the output directory including the location
    context group name in the path.
    :param paths:
    :param group_name:
    :param out_path:
    :return:
    """
    for path in paths:
        # parse the paths
        file_path = path.get('file_path')
        parts = path.get('path_parts')
        source_type = parts.get("source_type")
        year = parts.get("year")
        month = parts.get("month")
        day = parts.get("day")
        location = parts.get("location")
        data_type = parts.get("data_type")
        remainder = parts.get("remainder")
        # build the output path
        log.debug(f't: {source_type} Y: {year} M: {month} D: {day} '
                  f'loc: {location} type: {data_type} remainder: {remainder}')
        target_dir = os.path.join(out_path, source_type, year, month, day, group_name, location, data_type)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        destination = os.path.join(target_dir, *remainder[0:])
        # link the file
        log.debug(f'source: {file_path} destination: {destination}')
        file_linker.link(file_path, destination)


def main():
    """
    Add the related location group name stored in the location file to the output path.
    """
    env = environs.Env()
    source_path = env('SOURCE_PATH')
    group = env('GROUP')
    out_path = env('OUT_PATH')
    log_level = env('LOG_LEVEL')
    log_config.configure(log_level)
    log.debug(f'source_path: {source_path} group: {group} out_path: {out_path}')
    process(source_path, group, out_path)


if __name__ == '__main__':
    main()
