#!/usr/bin/env python3
import environs

import common.log_config

from date_gap_filler.data_file_path_config import DataFilePathConfig
from date_gap_filler.location_file_path_config import LocationFilePathConfig
from date_gap_filler.date_gap_filler_config import DateGapFillerConfig
from date_gap_filler.date_gap_filler import DateGapFiller


def main():
    env = environs.Env()
    data_path = env.path('DATA_PATH', None)
    location_path = env.path('LOCATION_PATH', None)
    empty_file_path = env.path('EMPTY_FILE_PATH')
    out_path = env.path('OUT_PATH')
    start_date = env.date('START_DATE', None)
    end_date = env.date('END_DATE', None)
    output_directories = env.list('OUTPUT_DIRECTORIES')
    data_source_type_index = env.int('DATA_SOURCE_TYPE_INDEX')
    data_year_index = env.int('DATA_YEAR_INDEX')
    data_month_index = env.int('DATA_MONTH_INDEX')
    data_day_index = env.int('DATA_DAY_INDEX')
    data_location_index = env.int('DATA_LOCATION_INDEX')
    data_type_index = env.int('DATA_TYPE_INDEX')
    location_source_type_index = env.int('LOCATION_SOURCE_TYPE_INDEX')
    location_year_index = env.int('LOCATION_YEAR_INDEX')
    location_month_index = env.int('LOCATION_MONTH_INDEX')
    location_index = env.int('LOCATION_INDEX')
    empty_file_type_index = env.int('EMPTY_FILE_TYPE_INDEX')
    log_level = env.log_level('LOG_LEVEL', 'INFO')

    common.log_config.configure(log_level)

    data_file_path_config = DataFilePathConfig(source_type_index=data_source_type_index,
                                               year_index=data_year_index,
                                               month_index=data_month_index,
                                               day_index=data_day_index,
                                               location_index=data_location_index,
                                               data_type_index=data_type_index)
    location_file_path_config = LocationFilePathConfig(source_type_index=location_source_type_index,
                                                       year_index=location_year_index,
                                                       month_index=location_month_index,
                                                       location_index=location_index)
    config = DateGapFillerConfig(data_path=data_path,
                                 location_path=location_path,
                                 empty_file_path=empty_file_path,
                                 out_path=out_path,
                                 start_date=start_date,
                                 end_date=end_date,
                                 output_directories=output_directories,
                                 empty_file_type_index=empty_file_type_index)
    date_gap_filler = DateGapFiller(config=config,
                                    data_file_path_config=data_file_path_config,
                                    location_file_path_config=location_file_path_config)
    date_gap_filler.fill_gaps()


if __name__ == '__main__':
    main()
