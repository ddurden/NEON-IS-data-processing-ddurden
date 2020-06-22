#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
from typing import List

import structlog

import common.date_formatter as date_formatter
from common.location_file_parser import LocationFileParser


log = structlog.get_logger()


def link_location_files(*, location_path: Path, out_path: Path, schema_index: int):
    """
    Link a location file for each active date with path '/<schema>/yyyy/mm/dd/<location name>/<filename>'.

    :param location_path: The location file path.
    :param out_path: The output directory root path.
    :param schema_index: The file path index of the schema name.
    """
    for path in location_path.rglob('*'):
        if path.is_file():
            parts = path.parts
            schema_name: str = parts[schema_index]
            parser = LocationFileParser(path)
            location_name: str = parser.get_name()
            active_periods: List[dict] = parser.get_active_periods()
            for period in active_periods:
                start_date = period['start_date']
                end_date = period['end_date']
                log.debug(f'start_date: {start_date} end_date: {end_date}')
                if start_date is not None:
                    start_date = date_formatter.parse(start_date)
                if end_date is not None:
                    end_date = date_formatter.parse(end_date)
                for date in date_formatter.dates_between(start_date, end_date):
                    dt = datetime(date.year, date.month, date.day)
                    year, month, day = date_formatter.parse_date(dt)
                    link_path = Path(out_path, schema_name, year, month, location_name, path.name)
                    link_path.parent.mkdir(parents=True, exist_ok=True)
                    if not link_path.exists():
                        link_path.symlink_to(path)
