import os
from datetime import datetime
from pathlib import Path
from typing import List

from pyfakefs.fake_filesystem_unittest import TestCase

import common.date_formatter
from data_access.types.threshold import Threshold
from pub_files.database.queries.named_locations import NamedLocation
from pub_files.database.queries.value_list import Value
from pub_files.geometry import Geometry
from pub_files.input_files.file_metadata import PathElements, FileMetadata, DataFiles, DataFile
from pub_files.output_files.eml.eml_database import EmlDatabase
from pub_files.output_files.eml.eml_file import EmlFile
from pub_files.output_files.eml.external_eml_files import ExternalEmlFiles
from pub_files.publication_workbook import PublicationWorkbook
from pub_files.tests.file_processor_data.file_processor_database import get_data_product
from pub_files.tests.publication_workbook.publication_workbook import get_workbook
from pub_files.main import get_timestamp


class EmlTest(TestCase):

    def setUp(self) -> None:
        self.workbook = PublicationWorkbook(get_workbook())
        self.setUpPyfakefs()
        self.timestamp = get_timestamp()
        self.test_files_path = Path(os.path.dirname(__file__))
        self.out_path = Path('/out')
        self.fs.create_dir(self.out_path)
        self.domain = 'D10'
        self.site = 'CPER'
        self.year = '2020'
        self.month = '01'
        self.data_product_id = 'DP1.00041.01'
        self.add_boilerplate_file()
        self.add_contact_file()
        self.add_intellectual_rights_file()
        self.add_unit_types_file()

    def add_boilerplate_file(self) -> None:
        real_path = Path(self.test_files_path, 'boilerplate.xml')
        self.boilerplate_path = Path('/boilerplate.xml')
        self.fs.add_real_file(real_path, target_path=self.boilerplate_path)

    def add_contact_file(self) -> None:
        real_path = Path(self.test_files_path, 'contact.xml')
        self.contact_path = Path('/contact.xml')
        self.fs.add_real_file(real_path, target_path=self.contact_path)

    def add_intellectual_rights_file(self) -> None:
        real_path = Path(self.test_files_path, 'intellectual_rights.xml')
        self.intellectual_rights_path = Path('/intellectual_rights.xml')
        self.fs.add_real_file(real_path, target_path=self.intellectual_rights_path)

    def add_unit_types_file(self) -> None:
        real_path = Path(self.test_files_path, 'unit_types.xml')
        self.unit_types_path = Path('/unit_types.xml')
        self.fs.add_real_file(real_path, target_path=self.unit_types_path)

    def get_boilerplate(self) -> str:
        return self.boilerplate_path.read_text('UTF-8')

    def get_contact(self) -> str:
        return self.contact_path.read_text('UTF-8')

    def get_intellectual_rights(self) -> str:
        return self.intellectual_rights_path.read_text('UTF-8')

    def get_unit_types(self) -> str:
        return self.unit_types_path.read_text('UTF-8')

    @staticmethod
    def get_named_location(_name):
        return NamedLocation(location_id=138773,
                             name='CFGLOC101775',
                             description='Central Plains Soil Temp Profile SP2, Z6 Depth',
                             properties=[])

    @staticmethod
    def get_geometry(_name) -> Geometry:
        return Geometry(geometry='POINT Z (-104.745591 40.815536 1653.9151)', srid=4979)

    @staticmethod
    def get_unit_eml_type(_unit: str) -> str:
        return 'Custom'

    @staticmethod
    def get_spatial_unit(_srid: int) -> str:
        return 'meter'

    @staticmethod
    def get_value_list(_list_name: str) -> List[Value]:
        value = Value(id=1,
                      list_code='list_code',
                      name='value name',
                      rank=1,
                      code='code',
                      effective_date=get_timestamp(),
                      end_date=get_timestamp(),
                      publication_code='basic',
                      description='A test value for the list.')
        return [value]

    @staticmethod
    def get_thresholds(_term_name) -> List[Threshold]:
        threshold = Threshold(threshold_name='threshold_name',
                              term_name='term_name',
                              location_name='location_name',
                              context=['context_1', 'context_2', 'context_3'],
                              start_date=common.date_formatter.to_string(get_timestamp()),
                              end_date=common.date_formatter.to_string(get_timestamp()),
                              is_date_constrained=False,
                              start_day_of_year=100,
                              end_day_of_year=200,
                              number_value=100,
                              string_value='string_value')
        return [threshold]

    def test_write_file(self):
        elements = PathElements(domain=self.domain,
                                site=self.site,
                                year=self.year,
                                month=self.month,
                                data_product_id=self.data_product_id)
        now = datetime.now()
        data_file = DataFile(
                filename='NEON.D10.CPER.DP1.00041.001.210.000.000.prt.2020-03.expanded.20230405T190704Z.csv',
                description='A data file with data.',
                line_count=15
        )
        data_files = DataFiles(files=[data_file],
                               min_time=now,
                               max_time=now)
        data_product = get_data_product(self.fs, _data_product_id='unused')
        metadata = FileMetadata(path_elements=elements,
                                data_files=data_files,
                                data_product=data_product)
        database = EmlDatabase(get_geometry=self.get_geometry,
                               get_named_location=self.get_named_location,
                               get_spatial_unit=self.get_spatial_unit,
                               get_thresholds=self.get_thresholds,
                               get_unit_eml_type=self.get_unit_eml_type,
                               get_value_list=self.get_value_list)
        eml_files = ExternalEmlFiles(get_boilerplate=self.get_boilerplate,
                                     get_contact=self.get_contact,
                                     get_intellectual_rights=self.get_intellectual_rights,
                                     get_unit_types=self.get_unit_types)
        filename = EmlFile(out_path=self.out_path,
                           metadata=metadata,
                           eml_files=eml_files,
                           timestamp=self.timestamp,
                           database=database,
                           publication_workbook=self.workbook,
                           package_type='basic').write()
        assert Path(self.out_path, self.site, self.year, self.month, filename).exists()
