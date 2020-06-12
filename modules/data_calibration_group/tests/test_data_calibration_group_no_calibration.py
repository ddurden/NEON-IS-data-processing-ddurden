#!/usr/bin/env python3
import os
from pathlib import Path

from pyfakefs.fake_filesystem_unittest import TestCase

from data_calibration_group.data_file_path import DataFilePath
from data_calibration_group.calibration_file_path import CalibrationFilePath
from data_calibration_group.data_calibration_grouper import DataCalibrationGrouper
import data_calibration_group.data_calibration_group_main as data_calibration_group_main


class DataCalibrationGroupNoCalibrationTest(TestCase):

    def setUp(self):
        self.setUpPyfakefs()

        in_path = Path('/inputs')
        self.out_path = Path('/outputs')
        self.calibration_path = in_path.joinpath('calibration')
        self.data_path = in_path.joinpath('data')
        self.data_metadata_path = Path('prt/2019/07/23/0001')
        self.calibration_metadata_path = Path('prt/0001')
        self.data_filename = 'prt_0001_2018-01-03.ext'

        self.fs.create_file(in_path.joinpath('data', self.data_metadata_path, self.data_filename))
        self.fs.create_dir(self.calibration_path.joinpath(self.calibration_metadata_path))

        self.data_source_type_index = 3
        self.data_year_index = 4
        self.data_month_index = 5
        self.data_day_index = 6
        self.calibration_source_type_index = 3
        self.calibration_source_id_index = 4
        self.calibration_stream_index = 5

    def test_group_files(self):
        data_file_path = DataFilePath(source_type_index=self.data_source_type_index,
                                      year_index=self.data_year_index,
                                      month_index=self.data_month_index,
                                      day_index=self.data_day_index)
        calibration_file_path = CalibrationFilePath(source_type_index=self.calibration_source_type_index,
                                                    source_id_index=self.calibration_source_id_index,
                                                    stream_index=self.calibration_stream_index)
        data_calibration_grouper = DataCalibrationGrouper(data_path=self.data_path,
                                                          calibration_path=self.calibration_path,
                                                          out_path=self.out_path,
                                                          data_file_path=data_file_path,
                                                          calibration_file_path=calibration_file_path)
        data_calibration_grouper.group_files()
        self.check_output()

    def test_app(self):
        os.environ['DATA_PATH'] = str(self.data_path)
        os.environ['CALIBRATION_PATH'] = str(self.calibration_path)
        os.environ['OUT_PATH'] = str(self.out_path)
        os.environ['LOG_LEVEL'] = 'DEBUG'
        os.environ['DATA_SOURCE_TYPE_INDEX'] = str(self.data_source_type_index)
        os.environ['DATA_YEAR_INDEX'] = str(self.data_year_index)
        os.environ['DATA_MONTH_INDEX'] = str(self.data_month_index)
        os.environ['DATA_DAY_INDEX'] = str(self.data_day_index)
        os.environ['CALIBRATION_SOURCE_TYPE_INDEX'] = str(self.calibration_source_type_index)
        os.environ['CALIBRATION_SOURCE_ID_INDEX'] = str(self.calibration_source_id_index)
        os.environ['CALIBRATION_STREAM_INDEX'] = str(self.calibration_stream_index)
        data_calibration_group_main.main()
        self.check_output()

    def check_output(self):
        root_path = Path(self.out_path, self.data_metadata_path)
        calibration_path = root_path.joinpath('calibration')
        data_path = root_path.joinpath('data', self.data_filename)
        metadata_path = calibration_path.joinpath(self.calibration_metadata_path)
        self.assertTrue(calibration_path.exists())
        self.assertTrue(data_path.exists())
        self.assertFalse(metadata_path.exists())
