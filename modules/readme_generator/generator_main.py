#!/usr/bin/env python3
from contextlib import closing
from pathlib import Path

from structlog import get_logger
import environs

from common import log_config
from data_access.db_config_reader import read_from_mount
from data_access.db_connector import DbConnector
from readme_generator.file_descriptions import get_descriptions
from readme_generator.location_geometry import get_geometry
from readme_generator.log_entry import get_log_entries
from readme_generator.data_product import get_data_product
from readme_generator.data_product_keyword import get_keywords
from readme_generator.generator import generate_readme, Config


def make_get_data_product(connector: DbConnector):
    def f(dp_idq: str):
        return get_data_product(connector, dp_idq)
    return f


def make_get_keywords(connector: DbConnector):
    def f(dp_idq: str):
        return get_keywords(connector, dp_idq)
    return f


def make_get_log_entries(connector: DbConnector):
    def f(dp_idq: str):
        return get_log_entries(connector, dp_idq)
    return f


def make_get_geometry(connector: DbConnector):
    def f(dp_idq: str):
        return get_geometry(connector, dp_idq)
    return f


def make_get_descriptions(connector: DbConnector):
    def f():
        return get_descriptions(connector)
    return f


def main() -> None:
    env = environs.Env()
    in_path: Path = env.path('IN_PATH')
    out_path: Path = env.path('OUT_PATH')
    template_path: Path = env.path('TEMPLATE_PATH')
    log_level: str = env.log_level('LOG_LEVEL', 'INFO')
    log_config.configure(log_level)
    log = get_logger()
    log.debug(f'out_path: {out_path}')
    config = Config(
        in_path=in_path,
        out_path=out_path,
        template_path=template_path)
    db_config = read_from_mount(Path('/var/db_secret'))
    with closing(DbConnector(db_config)) as connector:
        generate_readme(config=config,
                        get_log_entries=make_get_log_entries(connector),
                        get_data_product=make_get_data_product(connector),
                        get_geometry=make_get_geometry(connector),
                        get_descriptions=make_get_descriptions(connector),
                        get_keywords=make_get_keywords(connector))


if __name__ == '__main__':
    main()
