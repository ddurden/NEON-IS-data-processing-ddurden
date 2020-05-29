#!/usr/bin/env python3
import environs
from structlog import get_logger

from lib import log_config as log_config

from padded_timeseries_analyzer.padded_timeseries_analyzer.analyzer import PaddedTimeSeriesAnalyzer


def main():
    """Analyze padded time series data"""
    env = environs.Env()
    data_path = env.path('DATA_PATH')
    out_path = env.path('OUT_PATH')
    log_level = env.log_level('LOG_LEVEL')
    relative_path_index = env.int('RELATIVE_PATH_INDEX')
    log_config.configure(log_level)
    log = get_logger()
    log.debug(f'data_path: {data_path} out_path: {out_path}')
    analyzer = PaddedTimeSeriesAnalyzer(data_path, out_path, relative_path_index)
    analyzer.analyze()


if __name__ == '__main__':
    main()
