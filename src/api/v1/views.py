from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1 import serializers
from api.v1.filters import ForecastFilter, SaleFilter
from api.v1.serializers import UserSerializer
from forecasts.models import SKU, Forecast, Sale, Store
from users.models import User


class SKUViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A view set for the SKU model.

    This view set provides read-only access to the SKU model.
    """

    queryset = SKU.objects.all()
    serializer_class = serializers.SKUSerializer


class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A view set for the Store model.

    This view set provides read-only access to the Store model.
    """

    queryset = Store.objects.all()
    serializer_class = serializers.StoreSerializer


class SaleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A view set for the Sale model.

    This view set provides read-only access to the Sale model
    and supports filtering.
    """

    queryset = Sale.objects.all()
    serializer_class = serializers.SaleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SaleFilter


class ForecastViewSet(viewsets.ModelViewSet):
    """
    A view set for the Forecast model.

    This view set provides both read and write access to the Forecast model
    and supports filtering.
    """

    queryset = Forecast.objects.all()
    serializer_class = serializers.ForecastSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ForecastFilter


class UserViewSet(viewsets.GenericViewSet):
    """User model view set."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=("get",), detail=False)
    def me(self, request, *args, **kwargs):
        """Retrieve the authenticated user's information."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
