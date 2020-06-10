#!/usr/bin/env python3
from pathlib import Path

import structlog

from common.data_filename import DataFilename

log = structlog.get_logger()


class DataLocationGrouper(object):

    def __init__(self, *, data_path: Path, location_path: Path, out_path: Path,
                 source_type_index: int,
                 year_index: int,
                 month_index: int,
                 day_index: int,
                 file_index: int):
        """
        Constructor.

        :param data_path: The path to the data files.
        :param location_path: The path to the location files.
        :param out_path: The output path to link grouped files.
        :param source_type_index: The file path source type index.
        :param year_index: The file path year index.
        :param month_index: The file path month index.
        :param day_index: The file path day index.
        :param file_index: The file path file index.
        """
        self.data_path = data_path
        self.location_path = location_path
        self.out_path = out_path
        self.source_type_index = source_type_index
        self.year_index = year_index
        self.month_index = month_index
        self.day_index = day_index
        self.file_index = file_index

    def group_files(self):
        for common_output_path in self.link_data_files():
            self.link_location_files(common_output_path)

    def link_data_files(self):
        """
        Link data files into the output path and yield the output directory.

        :return: Yields the output directory path for each data file.
        """
        for path in self.data_path.rglob('*'):
            if path.is_file():
                parts = path.parts
                source_type = parts[self.source_type_index]
                year = parts[self.year_index]
                month = parts[self.month_index]
                day = parts[self.day_index]
                filename = parts[self.file_index]
                source_id = DataFilename(filename).source_id()
                common_output_path = Path(self.out_path, source_type, year, month, day, source_id)
                link_path = Path(common_output_path, 'data', filename)
                log.debug(f'link path: {link_path}')
                link_path.parent.mkdir(parents=True, exist_ok=True)
                link_path.symlink_to(path)
                yield common_output_path

    def link_location_files(self, common_output_path: Path):
        """
        Link the location files.

        :param common_output_path: The common output path from data file path elements.
        """
        for path in self.location_path.rglob('*'):
            if path.is_file():
                link_path = Path(common_output_path, 'location', path.name)
                log.debug(f'location link path: {link_path}')
                link_path.parent.mkdir(parents=True, exist_ok=True)
                link_path.symlink_to(path)
