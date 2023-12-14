from pathlib import Path

from maintenance_table_loader.field_loader import Field
from maintenance_table_loader.parquet_file_writer import write_file as write_parquet
from maintenance_table_loader.csv_file_writer import write_file as write_csv
from maintenance_table_loader.result_values_loader import ResultValue
from maintenance_table_loader.result_loader import Result
from maintenance_table_loader.table_data import ResultValues, FieldValue, TableData


def load_files(out_path: Path, data_reader, file_type) -> None:
    for table in data_reader.get_tables():
        fields: list[Field] = data_reader.get_fields(table)
        results: list[Result] = data_reader.get_results(table)
        table_results: list[ResultValues] = []
        for result in results:
            values_by_field_id: dict[[int], ResultValue] = data_reader.get_result_values(result)
            field_values: list[FieldValue] = []
            for field in fields:
                try:
                    result_value: ResultValue = values_by_field_id[field.field_id]
                    field_values.append(FieldValue(field=field, value=result_value))
                except KeyError:
                    field_values.append(FieldValue(field=field, value=None))
            table_results.append(ResultValues(result=result, values=field_values))
        table_data = TableData(table=table, fields=fields, results=table_results)
        if results:
            if file_type == 'csv':
                write_csv(out_path, table_data)
            if file_type == 'parquet':
                write_parquet(out_path, table_data)
