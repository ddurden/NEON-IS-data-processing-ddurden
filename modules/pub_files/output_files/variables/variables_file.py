import csv
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import structlog

from pub_files.database.file_variables import FileVariables
from pub_files.database.publication_workbook import PublicationWorkbook, WorkbookRow
from pub_files.input_files.file_metadata import FileMetadata, DataFile
from pub_files.output_files.filename_format import get_filename
from pub_files.output_files.science_review.science_review_file import ScienceReviewFile, Term
from pub_files.output_files.variables.variables_database import VariablesDatabase

log = structlog.get_logger()


def write_file(out_path: Path,
               file_metadata: FileMetadata,
               workbook: PublicationWorkbook,
               timestamp: datetime,
               science_review_file: Optional[ScienceReviewFile],
               database: VariablesDatabase) -> Path:
    """
    Generate and write the variables file into the output path.

    :param out_path: The output path for writing the file.
    :param file_metadata: The metadata from processing the application input files.
    :param workbook: The publication workbook for the data product being published.
    :param timestamp: The timestamp to include in the filename.
    :param science_review_file: An object containing the science review file Path and term names.
    :param database: A class with functions for reading from the database.
    """
    filename = get_filename(file_metadata.path_elements, timestamp=timestamp, file_type='variables', extension='csv')
    path = Path(out_path, filename)
    with open(path, 'w', encoding='UTF8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['table', 'fieldName', 'description', 'dataType', 'units', 'downloadPkg', 'pubFormat'])
        write_rows(writer, workbook.workbook_rows)
        write_sensor_positions_variables(writer, database.get_sensor_position_variables())
        if science_review_file is not None:
            write_science_review_variables(writer, file_metadata.data_files.files, science_review_file.terms,
                                           database)
    return path


def write_rows(writer, rows: List[WorkbookRow]) -> None:
    for row in rows:
        table_name = row.table_name
        field_name = row.field_name
        description = row.description
        data_type = row.data_type_code
        units = row.unit_name
        download_package = row.download_package
        publication_format = row.publication_format
        if download_package != 'none':
            values = [table_name, field_name, description, data_type, units, download_package, publication_format]
            writer.writerow(values)


def write_sensor_positions_variables(writer, file_variables: List[FileVariables]) -> None:
    """
    Read the variables and add them to the variables file.

    :param writer: The file writer.
    :param file_variables: List of sensor position variables.
    """
    for file_variable in file_variables:
        table_name = file_variable.table_name
        description = file_variable.description
        term_name = file_variable.term_name
        download_package = file_variable.download_package
        publication_format = file_variable.publication_format
        data_type = file_variable.data_type
        units = file_variable.units
        row = [table_name, term_name, description, data_type, units, download_package, publication_format]
        writer.writerow(row)


def write_science_review_variables(writer, data_files: List[DataFile], terms: List[Term],
                                   database: VariablesDatabase) -> None:
    """Add the science review terms to the variables file."""
    table_name = 'science_review_flags'
    rows = []
    for term in terms:
        log.debug(f'Processing term: {term.name}')
        for data_file in data_files:
            log.debug(f'Processing data_file: {data_file.filename}')
            data_product_name = format_data_product_name(data_file.data_product_name, term.number)
            term_variables = database.get_term_variables(data_product_name, term.name)
            description = term_variables.description
            data_type = term_variables.data_type
            units = term_variables.units
            term_download_package = term_variables.download_package
            publication_format = term_variables.publication_format
            row = [table_name, term.name, description, data_type, units, term_download_package, publication_format]
            if row not in rows:
                rows.append(row)
    writer.writerows(rows)


def format_data_product_name(data_product_name: str, term_number: str) -> str:
    """
    Converts a data product name from the data filename form:
    NEON.D10.CPER.DP1.00041.01.001.002.030
    to the more general form used with the term number specified in the pub_field_def table:
    NEON.DOM.SITE.DP1.00041.01.00461.HOR.VER.001.
    """
    parts = data_product_name.split('.')
    parts[1] = 'DOM'
    parts[2] = 'SITE'
    parts[6] = 'HOR'
    parts[7] = 'VER'
    parts.insert(6, term_number)
    return '.'.join(parts)
