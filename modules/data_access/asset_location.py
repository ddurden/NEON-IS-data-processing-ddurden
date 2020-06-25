from typing import NamedTuple, List
from datetime import datetime

from geojson import FeatureCollection

from data_access.property import Property


class AssetLocation(NamedTuple):
    name: str
    site: str
    install_date: datetime
    remove_date: datetime
    transaction_date: datetime
    context: List[str]
    properties: List[Property]
    locations: FeatureCollection
