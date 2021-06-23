#!/usr/bin/env python3
from structlog import get_logger
import environs
from pathlib import Path
import os

import common.log_config as log_config
from transformer.transformer import transform

log = get_logger()


def main() -> None:
    """
    Link input paths into the output path.
    """
    env = environs.Env()
    related_paths: list = env.list('RELATED_PATHS')
    data_path: Path = env.path('DATA_PATH')
    location_path: Path = env.path('LOCATION_PATH')
    out_path: Path = env.path('OUT_PATH')
    log_level: str = env.log_level('LOG_LEVEL', 'INFO')
    relative_path_index: int = env.int('RELATIVE_PATH_INDEX')
    year_index: int = env.int('YEAR_INDEX')
    month_index: int = env.int('MONTH_INDEX')
    loc_index: int = env.int('LOC_INDEX')
    log_config.configure(log_level)
    log.debug(f'related_paths: {related_paths} out_path: {out_path}')
    paths = []
    for p in related_paths:
        path = os.environ[p]
        paths.append(Path(path))
    transform(related_paths=paths, data_path=data_path, location_path=location_path, out_path=out_path, 
              relative_path_index=relative_path_index, 
              year_index=year_index, month_index=month_index, loc_index=loc_index)

if __name__ == '__main__':
    main()
