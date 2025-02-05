#!/usr/bin/env python3
from pathlib import Path
from typing import Callable, Iterator

from geojson import FeatureCollection, dumps
import structlog

from data_access.types.asset import Asset

log = structlog.get_logger()


def write_files(*,
                get_assets: Callable[[str], Iterator[Asset]],
                get_asset_locations: Callable[[Asset], FeatureCollection],
                out_path: Path,
                source_type: str) -> None:
    """
    Write GEOJson files of assets and their locations.

    :param get_assets: Function returning a list of assets.
    :param get_asset_locations: Function taking an Asset and returning a FeatureCollection of asset locations.
    :param out_path: Path for writing files.
    :param source_type: The data source type.
    """
    for asset in get_assets(source_type=source_type):
        log.debug(f'Processing asset: {asset.id}')
        locations: FeatureCollection = get_asset_locations(asset=asset)
        write_file(asset=asset, locations=locations, out_path=out_path)


def write_file(*, asset: Asset, locations: FeatureCollection, out_path: Path) -> None:
    """
    Write a GEOJson file of the asset and its locations.

    :param asset: The asset.
    :param locations: The asset's location history.
    :param out_path: The path for writing files.
    """
    geojson_data = dumps(locations, indent=4, sort_keys=True, default=str)
    file_name = f'{asset.type}_{str(asset.id)}_locations.json'
    file_path = Path(out_path, asset.type, str(asset.id), file_name)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as location_file:
        location_file.write(geojson_data)
