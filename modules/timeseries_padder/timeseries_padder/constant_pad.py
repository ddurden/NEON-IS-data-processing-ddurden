#!/usr/bin/env python3
from pathlib import Path
import datetime
from typing import Dict, List

from structlog import get_logger

import timeseries_padder.timeseries_padder.pad_calculator as pad_calculator
import timeseries_padder.timeseries_padder.file_writer as file_writer
from timeseries_padder.timeseries_padder.timeseries_padder_config import Config
from timeseries_padder.timeseries_padder.data_path_parser import DataPathParser

log = get_logger()


class ConstantPad:
    """Class to pad data with a fixed window size."""

    def __init__(self, config: Config) -> None:
        self.data_path = config.data_path
        self.out_path = config.out_path
        self.relative_path_index = config.relative_path_index
        self.window_size = config.window_size
        self.year_index = config.year_index
        self.month_index = config.month_index
        self.day_index = config.day_index
        self.location_index = config.location_index
        self.process_types = [config.data_dir]
        self.out_path_parts = list(config.out_path.parts)
        self.data_path_parser = DataPathParser(config)

    def pad(self) -> None:
        """Pad the data using the given window size."""
        manifests: Dict[str, List[datetime]] = {}
        manifest_file_names: Dict[str, Path] = {}
        for path in self.data_path.rglob('*'):
            if path.is_file():
                self.process_file(path, manifests, manifest_file_names)
        file_writer.write_manifests(manifests, manifest_file_names)

    def process_file(self, path: Path, manifests: dict, manifest_file_names: dict) -> None:
        """
        Process each data file by linking into each date in the padded time range,
        linking the threshold file, and the manifest file containing the padded dates.

        :param path: The data file path.
        :param manifests: The manifest dates organized by location.
        :param manifest_file_names:  The manifest file names organized by location.
        """
        parts = path.parts
        year, month, day, location, data_type = self.data_path_parser.parse(path)
        if data_type in self.process_types:
            location_path = Path(*parts[:self.location_index + 1])
            if location not in manifests:
                manifests[f'{location}_{day}'] = []
            data_date = datetime.date(int(year), int(month), int(day))
            padded_range_dates = pad_calculator.get_padded_dates(data_date, self.window_size)
            # link file into each date in the padded range
            link_parts = list(parts)
            for index in range(1, len(self.out_path_parts)):
                link_parts[index] = self.out_path_parts[index]
            for date in padded_range_dates:
                link_parts[self.year_index] = str(date.year)
                link_parts[self.month_index] = str(date.month).zfill(2)
                link_parts[self.day_index] = str(date.day).zfill(2)
                link_path = Path(*link_parts)
                log.debug(f'file: {path} link: {link_path}')
                link_path.parent.mkdir(parents=True, exist_ok=True)
                if not link_path.exists():
                    link_path.symlink_to(path)
                manifests[f'{location}_{day}'].append(date)
                if date == data_date:
                    manifest_file_names[f'{location}_{day}'] = Path(link_path.parent, Config.manifest_filename)
                file_writer.link_thresholds(location_path, link_path)
        else:
            link_path = Path(self.out_path, *parts[self.relative_path_index:])
            link_path.parent.mkdir(parents=True, exist_ok=True)
            if not link_path.exists():
                link_path.symlink_to(path)
