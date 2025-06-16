# http://stackoverflow.com/questions/12507274/how-to-get-bounds-of-a-google-static-map
import math

from PyQt6.QtCore import QPointF


def bound(value, opt_min, opt_max):
    if (opt_min is not None):
        value = max(value, opt_min)
    if (opt_max is not None):
        value = min(value, opt_max)
    return value

def degreesToRadians(deg):
    return deg * (math.pi / 180)

def radiansToDegrees(rad):
    return rad / (math.pi / 180)

class LatLng:
    def __init__(self, lt: float, ln: float):
        self.lat = lt
        self.lng = ln

    def __repr__(self):
        return "LatLng(%g,%g)" % (self.lat, self.lng)

    def __str__(self):
        return "(lat=%g,lng=%g)" % (self.lat, self.lng)


class MercatorProjection:

    def __init__(self):
        self.pixel_origin = QPointF(Utils.MERCATOR_RANGE / 2.0, Utils.MERCATOR_RANGE / 2.0)
        self.pixels_per_long_degree = Utils.MERCATOR_RANGE / 360.0
        self.pixels_per_long_radian = Utils.MERCATOR_RANGE / (2.0 * math.pi)

    def fromLatLngToPoint(self, lat_lng: LatLng, point:QPointF = QPointF(0, 0)) -> QPointF:
        point.x = self.pixel_origin.x() + lat_lng.lng * self.pixels_per_long_degree
        # NOTE(appleton): Truncating to 0.9999 effectively limits latitude to
        # 89.189.This is about a third of a tile past the edge of world tile
        sin_y = bound(math.sin(degreesToRadians(lat_lng.lat)), -0.9999, 0.9999)
        point.y = self.pixel_origin.y() + 0.5 * math.log((1 + sin_y) / (1.0 - sin_y)) * -self.pixels_per_long_radian
        return point

    def fromPointToLatLng(self, point: QPointF) -> LatLng:
        origin = self.pixel_origin
        longitude = (point.x() - origin.x()) / self.pixels_per_long_degree
        lat_radians = (point.y() - origin.y()) / -self.pixels_per_long_radian
        latitude = radiansToDegrees(2.0 * math.atan(math.exp(lat_radians)) - math.pi / 2.0)
        return LatLng(latitude, longitude)

class Utils:
    MERCATOR_RANGE = 256

    @staticmethod
    def getCorners(
            center: LatLng,
            zoom: int,
            map_width: int,
            map_height: int
    ):
        scale = 2.0**zoom
        projection = MercatorProjection()
        center_point = projection.fromLatLngToPoint(center)
        sw_point = QPointF(
            center_point.x - (map_width / 2.0) / scale,
            center_point.y + (map_height / 2.0) / scale
        )
        sw_lat_long = projection.fromPointToLatLng(sw_point)

        ne_point = QPointF(
            center_point.x + (map_width / 2.0) / scale,
            center_point.y - (map_height / 2.0) / scale
        )
        ne_lat_long = projection.fromPointToLatLng(ne_point)

        return {
            'N': ne_lat_long.lat,
            'E': ne_lat_long.lng,
            'S': sw_lat_long.lat,
            'W': sw_lat_long.lng,
        }

    # https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
    @staticmethod
    def getTileXY(lat_long: LatLng, zoom: int):
        latitude_radians = math.radians(lat_long.lat)
        n = 2.0 ** zoom
        xtile = (lat_long.lng + 180.0) / 360.0 * n
        ytile = ((1.0 - math.log(math.tan(latitude_radians) +
                 (1 / math.cos(latitude_radians))) / math.pi) / 2.0 * n)
        return {
            'X': xtile,
            'Y': ytile
        }