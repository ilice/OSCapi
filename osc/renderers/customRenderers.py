from rest_framework import renderers

from osc.models.parcel import featurestoGeoJSON
from osc.models.parcel import GeoJSON


class GeoJSONRenderer(renderers.BaseRenderer):
    media_type = 'application/json'
    format = 'geoJSON'

    def render(self, data, media_type=None, renderer_context=None):
        return GeoJSON(data)
