#!/usr/bin/env python3
from pathlib import Path
from structlog import get_logger

import environs
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from flow_sae_trst_dp0p.cal_flags import get_cal_val_flags
from flow_sae_trst_dp0p import log_config
from typing import List, Dict, Optional, Hashable

log = get_logger()


class L0toL0p:
    """
    base class for SAE L0 to L0p data transformation
    """

    def __init__(self, cal_term_map: Optional[Dict] = None, calibrated_qf_list: Optional[List] = None,
                 target_qf_cal_list: Optional[List] = None):
        """
        :param cal_term_map: map for calibrated variables between field names from avro schema and term names from ATBD
        :param calibrated_qf_list: list of quality flag names that were calibrated on site
        :param target_qf_cal_list: list of quality flag names that will take flags from calibrated_qf_list
        environment variables:
        in_path: The input path for files.
        out_path: The output path for linking.
        file_dirs: The directories to files need l0 to l0p transformation.
        relative_path_index: Starting index of the input path to include in the output path.
        new_source_type_name: Replace source_type with the new name in the output path,
                may happen when multiple data products derived from same sensor type,
                e.g. mcseries -> mfcSampTurb
        When new_source_type_name is defined, relative_path_index is the index after that of replaced source type
       """
        self.cal_term_map = cal_term_map or {}
        self.calibrated_qf_list = calibrated_qf_list or []
        self.target_qf_cal_list = target_qf_cal_list or []
        env = environs.Env()
        self.in_path: Path = env.path('IN_PATH')
        self.out_path: Path = env.path('OUT_PATH')
        self.file_dirs: list = env.list('FILE_DIR')
        self.relative_path_index: int = env.int('RELATIVE_PATH_INDEX')
        self.new_source_type_name: str = env.str('NEW_SOURCE_TYPE_NAME', None)
        log_level: str = env.log_level('LOG_LEVEL', 'DEBUG')
        log_config.configure(log_level)

    def data_conversion(self, filename) -> pd.DataFrame:
        out_df = pd.read_parquet(filename)
        log.debug(f'{out_df.columns}')
        log.info(out_df['site_id'][1])
        log.info(out_df['source_id'][1])
        # drop columns not used in l0 to l0p data conversion
        self.drop_kafka_columns(out_df)
        return out_df

    @staticmethod
    def drop_kafka_columns(in_df: pd.DataFrame) -> None:
        kafka_columns = ['kafka_key', 'kafka_topic', 'kafka_partition', 'kafka_offset', 'kafka_ts', 'kakfa_ts_type']
        if kafka_columns[0] in in_df.columns:
            in_df.drop(columns=kafka_columns, inplace=True)

    def get_combined_qfcal(self, out_df: pd.DataFrame) -> None:
        if len(self.calibrated_qf_list) == 0:
            return
        elif len(self.calibrated_qf_list) == 1:
            self.assign_qf_cal(out_df[self.calibrated_qf_list[0]], out_df)
        else:
            qf = 0
            for qfcal in self.calibrated_qf_list:
                if qfcal == 1:
                    qf = 1
                    break
                elif qfcal == -1:
                    qf = -1
            self.assign_qf_cal(qf, out_df)

    def assign_qf_cal(self, qf, out_df):
        for qfname in self.target_qf_cal_list:
            out_df[qfname] = qf

    def l0tol0p(self) -> None:
        """
        L0 to l0p transformation.
        """
        out_df = pd.DataFrame()
        out_file = ''
        for root, directories, files in os.walk(str(self.in_path)):
            if root.endswith('location'):
                continue
            if not out_df.empty and len(directories) > 0:
                if any(tmp_dir in directories for tmp_dir in self.file_dirs):
                    self.write_to_parquet(out_file, out_df)
                    out_df = pd.DataFrame()
                    out_file = ''
            if len(files) > 0:
                if len(files) > 1:
                    log.warn("There are more than 1 files under " + root)
                    log.warn(files)
                for file in files:
                    path = Path(root, file)
                    if "flag" in str(path):
                        if out_df.empty:
                            out_df = get_cal_val_flags(path, self.cal_term_map)
                        else:
                            out_df = pd.merge(out_df, get_cal_val_flags(path, self.cal_term_map), how='inner',
                                              left_on=['readout_time'], right_on=['readout_time'])
                        self.get_combined_qfcal(out_df)
                    else:
                        if self.new_source_type_name:
                            out_file = Path(self.out_path, Path(self.new_source_type_name),
                                            *Path(path).parts[self.relative_path_index:])
                        else:
                            out_file = Path(self.out_path, *Path(path).parts[self.relative_path_index:])
                        out_file.parent.mkdir(parents=True, exist_ok=True)
                        if out_df.empty:
                            out_df = self.data_conversion(path)
                        else:
                            out_df = pd.merge(self.data_conversion(path), out_df, how='inner', left_on=['readout_time'],
                                              right_on=['readout_time'])
        if not out_df.empty and out_file != '':
            self.write_to_parquet(out_file, out_df)

    @staticmethod
    def write_to_parquet(out_file: str, out_df: pd.DataFrame) -> None:
        hashable_cols = [x for x in out_df.columns if isinstance(out_df[x].iloc[0], Hashable)]
        dupcols = [x.encode('UTF-8') for x in hashable_cols
                   if (out_df[x].duplicated().sum() / (int(out_df[x].size) - 1)) > 0.3]
        table = pa.Table.from_pandas(out_df)
        pq.write_table(table, out_file, use_dictionary=dupcols, version="2.4", compression='zstd', compression_level=8,
                       coerce_timestamps='ms', allow_truncated_timestamps=False)
        # out_df.to_parquet(out_file, use_dictionary=dupcols, version="2.4", compression='zstd', compression_level=8,
        #                   coerce_timestamps='ms', allow_truncated_timestamps=False)
