#!/usr/bin/env python3
import environs
import structlog
from contextlib import closing
from pathlib import Path
from functools import partial

import common.log_config as log_config
from data_access.db_config_reader import read_from_mount
from data_access.db_connector import DbConnector
from data_access.get_assets import get_assets
from data_access.get_asset_locations import get_asset_locations

import location_asset_loader.location_asset_loader as location_asset_loader

log = structlog.get_logger()


def main() -> None:
    env = environs.Env()
    source_type: str = env.str('SOURCE_TYPE')
    out_path: Path = env.path('OUT_PATH')
    log_level: str = env.log_level('LOG_LEVEL', 'INFO')
    log_config.configure(log_level)
    log.debug(f'out_path: {out_path}')
    db_config = read_from_mount(Path('/var/db_secret'))
    with closing(DbConnector(db_config)) as connector:
        get_assets_partial = partial(get_assets, connector)
        get_asset_locations_partial = partial(get_asset_locations, connector)
        location_asset_loader.write_files(get_assets=get_assets_partial,
                                          get_asset_locations=get_asset_locations_partial,
                                          out_path=out_path,
                                          source_type=source_type)


if __name__ == "__main__":
    main()
