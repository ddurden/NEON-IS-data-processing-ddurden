#!usr/bin/env python3
import os
import shutil
import glob
from structlog import get_logger
from pathlib import Path
from unittest import TestCase
from replace_macaddress_with_assetuid.replace_macaddress_with_assetuid import load_assetuid

log = get_logger()


class LoadAssetuidTest(TestCase):

    def setUp(self):
        self.data_path = Path('pfs/DATA_PATH')
        self.map_path = Path('pfs/MAP_PATH')
        self.out_path = Path('pfs/OUT_PATH')
        print(f'final output path is: {Path(self.out_path)}')
    #
    def test_load_assetuid(self):
        # clean up the output directory left from previous testing
        if os.path.exists(self.out_path):
            shutil.rmtree(self.out_path)
        load_assetuid(data_path = self.data_path, map_path = self.map_path, out_path = self.out_path)

        # asset_file_path = [f for f in listdir(self.map_path) if isfile(join(self.map_path,f))]
        # os.chdir(Path(asset_file_path))
        # asset_file_name = os.path.basename(__file__)
        # print('==== asset_file_name: ', asset_file_name)
        rootdir = 'pfs/OUT_PATH'
        for path in glob.glob(f'{rootdir}/*/**/', recursive=True):
            print(path)
            self.assertTrue(Path(path).exists())


if __name__ == '__main__':
    unittest()
