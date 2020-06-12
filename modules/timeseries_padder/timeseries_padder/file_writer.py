#!/usr/bin/env python3
from pathlib import Path
from structlog import get_logger

from timeseries_padder.timeseries_padder.pad_config import PadConfig


log = get_logger()


def write_manifests(manifests: dict, manifest_file_names: dict):
    """
    Write the manifest files.

    :param manifests: The manifests.
    :param manifest_file_names: The manifest file names.
    """
    for location in manifests.keys():
        with open(manifest_file_names[location], 'w') as manifest_file:
            for item in manifests[location]:
                manifest_file.write("%s\n" % item)


def link_thresholds(source_path: Path, destination_path: Path):
    """
    Link a threshold file if present in the source directory.

    :param source_path: The data file path.
    :param destination_path: The path to write the file.
    """
    threshold_file = Path(source_path, PadConfig.threshold_dir, PadConfig.threshold_filename)
    if threshold_file.exists():
        path = destination_path.parent.parent
        link_path = Path(path, PadConfig.threshold_dir, PadConfig.threshold_filename)
        log.debug(f'threshold file: {threshold_file} link: {link_path}')
        link_path.parent.mkdir(parents=True, exist_ok=True)
        if not link_path.exists():
            link_path.symlink_to(threshold_file)
