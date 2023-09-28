from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.v1 import serializers
from api.v1.filters import ForecastFilter, SaleFilter
from forecasts.models import SKU, Forecast, Sale, Store


class SKUViewSet(ReadOnlyModelViewSet):
    """
    A view set for the SKU model.

    This view set provides read-only access to the SKU model.
    """

    queryset = SKU.objects.all()
    serializer_class = serializers.SKUSerializer


class StoreViewSet(ReadOnlyModelViewSet):
    """
    A view set for the Store model.

    This view set provides read-only access to the Store model.
    """

    queryset = Store.objects.all()
    serializer_class = serializers.StoreSerializer


class SaleViewSet(ReadOnlyModelViewSet):
    """
    A view set for the Sale model.

    This view set provides read-only access to the Sale model
    and supports filtering.
    """

    queryset = Sale.objects.all()
    serializer_class = serializers.SaleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SaleFilter


class ForecastViewSet(ModelViewSet):
    """
    A view set for the Forecast model.

    This view set provides both read and write access to the Forecast model
    and supports filtering.
    """

    queryset = Forecast.objects.all()
    serializer_class = serializers.ForecastSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ForecastFilter
