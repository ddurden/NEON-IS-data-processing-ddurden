#!/usr/bin/env python3
from pathlib import Path
import json
import shutil

from structlog import get_logger

log = get_logger()


def pub_group(*, data_path: Path, out_path: Path, 
                 year_index: int, group_index: int, 
                 data_type_index: int, group_metadata_dir: str,
                 publoc_key: str, symlink: bool) -> None:
    """
    :param data_path: input data path
    :param out_path: output path
    :param year_index: index of year in data path
    :param group_index: index of group ID in data path. Each group ID is a datum.
    :param data_type_index: index of data & metadata directories in data path. Group metadata directory must be at this index.
    :param group_metadata_dir: directory name with group metadata (e.g. "group")
    :param publoc_key: identifier for publication grouping location in the group metadata json file (e.g. "site")
    :param symlink: Use a symlink to place files in the output (True) or use a straight copy (False) 
    """
    # Each group is a datum. Run through each group
    for path in data_path.rglob(group_metadata_dir + '/'):
        parts = path.parts
        group_metadata_name = parts[data_type_index]
        
        # Double check that the directory at the group metadata index matches the group directory name
        if group_metadata_name != group_metadata_dir:
            log.warn(f'Path {path.parent} looks to be a datum, but the directory at the group metadata index ({group_metadata_name}) does not match the expected name ({group_metadata_dir}). Skipping...')
            continue
        else:
            log.debug(f'Processing datum path {path.parent}')
        
        # Get the pub grouping location from the group metadata
        publoc = None
        products = None
        for group_metadata_path in path.rglob('*'):
            if group_metadata_path.is_file():
                f = open(str(group_metadata_path))
                group_data = json.load(f)
                publoc = group_data["features"][0][publoc_key]
                products = group_data["features"][0]["properties"]["data_product_ID"]
                f.close()
                break
            
        if publoc is None or products is None:
            log.error(f'Cannot determine publication grouping property from the files in {path}. Skipping.')
            continue
        if products is None:
            log.error(f'Cannot determine data products from the files in {path}. Skipping.')
            continue
        
        # Pass the group parent to the path iterator
        path = Path(*parts[0:group_index+1])    
        
        for subpath in path.rglob('*'):
            if subpath.is_file():
                parts = subpath.parts
                year = parts[year_index]
                month = parts[year_index+1]
                day = parts[year_index+2]
                group = parts[group_index]
                data_type = parts[data_type_index]
                data = parts[data_type_index+1:]
                
                for product in products:
                    new_path = out_path.joinpath(product,year,month,day,publoc,data_type,group,*data)
                    new_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if not new_path.exists():
                        if symlink:
                            log.debug(f'Linking path {new_path} to {subpath}.')
                            new_path.symlink_to(subpath)
                        else:
                            log.debug(f'Copying {subpath} to {new_path}.')
                            shutil.copy2(subpath,new_path)
                                    
