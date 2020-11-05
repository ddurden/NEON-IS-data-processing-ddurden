#!/usr/bin/env python3
import environs
import structlog
from pathlib import Path

import common.log_config as log_config

from array_parser.array_parser_config import Config
import array_parser.array_parser as array_parser

log = structlog.get_logger()


def main():
    env = environs.Env()
    data_path: Path = env.path('DATA_PATH')
    calibration_path: Path = env.path('CALIBRATION_PATH')
    out_path: Path = env.path('OUT_PATH')
    log_level: str = env.log_level('LOG_LEVEL', 'INFO')
    source_type_index: int = env.int('SOURCE_TYPE_INDEX')
    year_index: int = env.int('YEAR_INDEX')
    month_index: int = env.int('MONTH_INDEX')
    day_index: int = env.int('DAY_INDEX')
    source_id_index: int = env.int('SOURCE_ID_INDEX')
    data_type_index: int = env.int('DATA_TYPE_INDEX')
    log.debug(f'data_path: {data_path} calibration_path: {calibration_path} out_path: {out_path}')
    log_config.configure(log_level)
    config = Config(data_path=data_path,
                    calibration_path=calibration_path,
                    out_path=out_path,
                    source_type_index=source_type_index,
                    year_index=year_index,
                    month_index=month_index,
                    day_index=day_index,
                    source_id_index=source_id_index,
                    data_type_index=data_type_index)
    array_parser.parse(config)


if __name__ == '__main__':
    main()
