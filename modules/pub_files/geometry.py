from typing import Tuple


class Geometry:
    """Class to manage geolocation geometries as represented in the database."""

    def __init__(self, *, geometry, srid):
        """
        Constructor.

        :param geometry: The geometry string from the database.
        :param srid: The spatial reference identifier for the geometry.
        """
        self.geometry_text = geometry
        self.srid = srid
        (self.latitude, self.longitude, self.elevation) = self.get_coordinates()

    def get_coordinates(self) -> Tuple[float, float, float]:
        """Convert the geometry string to geo coordinates."""
        # POINT Z (-104.745591 40.815536 1653.9151)
        if self.geometry_text.startswith('POINT'):
            coordinates = self.geometry_text.split('(')[1].replace(')', '')
            parts = coordinates.split(' ')
        elif self.geometry_text.startswith('POLYGON'):
            # POLYGON Z ((-104.746013 40.815892 1654.009392,-104.745973 40.815922 1654.052064, ...))
            trimmed = self.geometry_text.split('((')[1].replace('))', '')
            first_point = trimmed.split(',')[0]
            parts = first_point.split(' ')
        else:
            raise Exception(f'Location geometry {self.geometry_text} is not point or polygon.')
        longitude = float(parts[0])
        latitude = float(parts[1])
        elevation = float(parts[2])
        return latitude, longitude, elevation

    def format_coordinates(self) -> str:
        """Return the coordinates in a string formatted for the readme file."""
        return f'{self.latitude} {self.longitude} WGS 84'
