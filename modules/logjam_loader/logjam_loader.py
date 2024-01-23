
from google.cloud import storage
from pathlib import Path
import environs
import os
import sys
from google.cloud import storage


def logjam_loader() -> None:

    env = environs.Env()
    ingest_bucket_name = env.str('LOGJAM_INGEST_BUCKET')
    output_directory: Path = env.path('OUT_PATH')
    storage_client = storage.Client()
    ingest_bucket = storage_client.bucket(ingest_bucket_name)
    path_names = storage_client.list_blobs(ingest_bucket)
    for blob in path_names:
        
        file_name = os.path.splitext(blob.name)[0]
        file_path = Path(output_directory, blob.updated.strftime("%Y"), blob.updated.strftime("%m"), blob.updated.strftime("%d"), file_name+".csv")         
        file_path.parent.mkdir(parents=True, exist_ok=True)
        print("File name is:  ", file_path)
        log_file= open(file_path, "w")
        log_file.write(blob.updated.strftime("%Y-%m-%d %H:%M:%S"))
        log_file.close()
        
if __name__ == '__main__':
    logjam_loader()
