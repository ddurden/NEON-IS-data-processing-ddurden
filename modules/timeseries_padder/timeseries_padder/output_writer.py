#!/usr/bin/env python3
import os

import pathlib
from structlog import get_logger

import lib.file_linker as file_linker


log = get_logger()


def write_manifests(manifests, manifest_file_names):
    for config_location in manifests.keys():
        with open(manifest_file_names[config_location], 'w') as f:
            for item in manifests[config_location]:
                f.write("%s\n" % item)


def write_thresholds(source_path, destination_path):
    threshold_dir = 'threshold'
    threshold_filename = 'thresholds.json'
    threshold_file = os.path.join(source_path, threshold_dir, threshold_filename)
    if pathlib.Path(threshold_file).exists():
        path = pathlib.Path(destination_path).parent.parent
        threshold_out = os.path.join(path, threshold_dir, threshold_filename)
        log.debug(f'Threshold file: {threshold_file}')
        log.debug(f'Threshold out: {threshold_out}')
        file_linker.link(threshold_file, threshold_out)
