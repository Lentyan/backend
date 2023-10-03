from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.v1 import filters, serializers
from api.v1.serializers import ForecastReportSerializer
from api.v1.utils.report_utils import generate_forecast_report
from forecasts import models
from users.models import User


class ListOnlyViewSet(mixins.ListModelMixin, GenericViewSet):
    """Base list only view set."""

    pagination_class = None
    list_key = "default_key"
    model_filed = None

    class ModelFieldNotSpecifiedError(Exception):
        """Exception raised when field is not specified."""

        def __init__(self, field_name):
            self.field_name = field_name
            super().__init__(f"Model field {field_name} is not specified.")

    def _get_unique_values(self, field_name, queryset=None):
        """Return unique values of models fields."""
        if queryset is None:
            queryset = self.queryset
        unique_values = (
            queryset.order_by().values_list(field_name, flat=True).distinct()
        )
        return unique_values

    def get_queryset(self):
        """Return queryset of unique values."""
        if self.model_filed is None:
            raise self.ModelFieldNotSpecifiedError("model_field")
        return self._get_unique_values(self.model_filed)

    def list(self, request, *args, **kwargs):
        """Return list of filtered unique values."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer({self.list_key: queryset})
        return Response(serializer.data)


class SKUViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A view set for the SKU model.

    This view set provides read-only access to the SKU model.
    """

    queryset = models.SKU.objects.all()
    serializer_class = serializers.SKUSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.SKUFilter


class GroupViewSet(ListOnlyViewSet):
    """
    A view set for the SKU groups.

    This view set provides read-only access to the SKU unique groups.
    """

    queryset = models.SKU.objects.all()
    serializer_class = serializers.GroupSerializer
    list_key = "groups"
    model_filed = "group"


class CategoryViewSet(ListOnlyViewSet):
    """
    A view set for the SKU groups.

    This view set provides read-only access to the SKU unique categories.
    """

    queryset = models.SKU.objects.all()
    serializer_class = serializers.CategorySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.CategoryFilter
    list_key = "categories"
    model_filed = "category"


class SubcategoryViewSet(ListOnlyViewSet):
    """
    A view set for the SKU groups.

    This view set provides read-only access to the SKU unique subcategories.
    """

    queryset = models.SKU.objects.all()
    serializer_class = serializers.SubcategorySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.SubcategoryFiler
    list_key = "subcategories"
    model_filed = "subcategory"


class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A view set for the Store model.

    This view set provides read-only access to the Store model.
    """

    queryset = models.Store.objects.all()
    serializer_class = serializers.StoreSerializer


class SaleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A view set for the Sale model.

    This view set provides read-only access to the Sale model
    and supports filtering.
    """

    queryset = models.Sale.objects.all()
    serializer_class = serializers.SaleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.SaleFilter


class ForecastViewSet(viewsets.ModelViewSet):
    """
    A view set for the Forecast model.

    This view set provides both read and write access to the Forecast model
    and supports filtering.
    """

    queryset = models.Forecast.objects.all()
    serializer_class = serializers.ForecastSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.ForecastFilter


class UserViewSet(viewsets.GenericViewSet):
    """User model view set."""

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    pagination_class = None

    @action(methods=("get",), detail=False)
    def me(self, request, *args, **kwargs):
        """Retrieve the authenticated user's information."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class GenerateForecastReport(GenericAPIView):
    """API view to generate forecast report."""

    serializer_class = ForecastReportSerializer

    def post(self, request, *args, **kwargs):
        """Post request handler."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid filter data"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = generate_forecast_report(serializer.validated_data)
        return response
