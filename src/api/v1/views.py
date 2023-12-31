import json

from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.v1 import filters, serializers
from forecasts import models
from forecasts.models import AsyncFileResults, Forecast
from forecasts.tasks import forecast_tasks
from forecasts.utils.csv_utils import import_data, read_csv_file
from forecasts.utils.report_utils import get_statistics_data
from users.models import User


class ListOnlyViewSet(mixins.ListModelMixin, GenericViewSet):
    """Base list only view set."""

    pagination_class = None
    list_key = "default_key"
    model_field = None

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
        if self.model_field is None:
            raise self.ModelFieldNotSpecifiedError("model_field")
        return self._get_unique_values(self.model_field)

    def list(self, request, *args, **kwargs):
        """Return list of filtered unique values."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer({self.list_key: queryset})
        return Response(serializer.data)


class GetOrCreateViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    """View set to create or get model instances."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = getattr(self, "model", None)
        if not self.model:
            raise AttributeError(
                "The 'model' attribute must be set on the viewset."
            )

    def paginate_queryset(self, queryset):
        """Turn off pagination is required."""
        if self.request.query_params.get("limit") == "false":
            return None
        return super().paginate_queryset(queryset)

    def get_queryset(self):
        """Return model queryset."""
        return self.model.objects.all()

    def get_serializer_class(self):
        """Return appropriate to method serializer."""
        raise NotImplementedError("Method must be implemented.")

    def create(self, request, *args, **kwargs):
        """Bulk create models."""
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            data_entries = serializer.validated_data.get("data", [])
            model_objects = [self.model(**attrs) for attrs in data_entries]
            instances = self.model.objects.bulk_create(
                model_objects,
                ignore_conflicts=True,
            )
            return Response(
                self.serializer_class(instances, many=True).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["post"],
        detail=False,
        serializer_class=serializers.CSVFileSerializer,
    )
    def create_from_csv(self, request):
        """
        Upload forecasts data from a CSV file.

        This action allows users to upload forecasts data from a CSV file.
        """
        serializer = serializers.CSVFileSerializer(data=request.data)
        if serializer.is_valid():
            csv_reader = read_csv_file(serializer.validated_data["csv_file"])
            import_data(self.model, csv_reader)
            return Response(
                {"message": "CSV is valid"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SKUViewSet(GetOrCreateViewSet):
    """
    A view set for the SKU model.

    This view set provides read-only access to the SKU model.
    """

    model = models.SKU
    serializer_class = serializers.SKUSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.SKUFilter

    def get_serializer_class(self):
        """Return appropriate to method serializer."""
        if self.request.method in SAFE_METHODS:
            return serializers.SKUSerializer
        return serializers.SKUPostSerializer


class GroupViewSet(ListOnlyViewSet):
    """
    A view set for the SKU groups.

    This view set provides read-only access to the SKU unique groups.
    """

    queryset = models.SKU.objects.all()
    serializer_class = serializers.GroupSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.GroupFilter
    list_key = "groups"
    model_field = "group"


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
    model_field = "category"


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
    model_field = "subcategory"


class StoreViewSet(GetOrCreateViewSet):
    """
    A view set for the Store model.

    This view set provides read-only access to the Store model.
    """

    model = models.Store
    serializer_class = serializers.StoreSerializer

    def get_serializer_class(self):
        """Return appropriate to method serializer."""
        if self.request.method in SAFE_METHODS:
            return serializers.StoreSerializer
        return serializers.StorePostSerializer


class SaleViewSet(GetOrCreateViewSet):
    """
    A view set for the Sale model.

    This view set provides read-only access to the Sale model
    and supports filtering.
    """

    model = models.Sale
    serializer_class = serializers.SaleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.SaleFilter

    def get_serializer_class(self):
        """Return appropriate to method serializer."""
        if self.request.method in SAFE_METHODS:
            return serializers.SaleSerializer
        return serializers.SalePostSerializer


class ForecastViewSet(GetOrCreateViewSet):
    """
    A view set for the Forecast model.

    This view set provides both read and write access to the Forecast model
    and supports filtering.
    """

    model = models.Forecast
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.ForecastFilter

    def get_serializer_class(self):
        """Return appropriate to method serializer."""
        if self.request.method in SAFE_METHODS:
            return serializers.ForecastSerializer
        return serializers.ForecastPostSerializer

    def get_queryset(self):
        """Return queryset of unique pairs of SKU and Store."""
        return self.model.objects.values("sku", "store").distinct()

    def create(self, request, *args, **kwargs):
        """Bulk create forecasts."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            forecasts_objects = [
                Forecast(**attrs)
                for attrs in serializer.validated_data.get("data")
            ]
            Forecast.objects.bulk_create(
                forecasts_objects,
                ignore_conflicts=True,
            )
            return Response(
                {"message": "created"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["post"],
        detail=False,
        serializer_class=serializers.CreateForecastReportSerializer,
        permission_classes=(IsAuthenticated,),
        filter_backends=None,
    )
    def generate_forecast_report(self, request, *args, **kwargs):
        """Generate forecast report."""
        serializer = serializers.CreateForecastReportSerializer(
            data=request.data,
        )
        if serializer.is_valid():
            task = forecast_tasks.generate_report.delay(
                request.user.id,
                serializer.validated_data,
                "forecast",
            )
            return Response(
                {"task_id": task.task_id}, status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=["post"],
        detail=False,
        serializer_class=serializers.CreateStatisticsReportSerializer,
        permission_classes=(IsAuthenticated,),
        filter_backends=None,
    )
    def generate_statistics_report(self, request, *args, **kwargs):
        """Generate forecast report."""
        serializer = serializers.CreateStatisticsReportSerializer(
            data=request.data,
        )
        if serializer.is_valid():
            task = forecast_tasks.generate_report.delay(
                request.user.id,
                serializer.validated_data,
                "statistics",
            )
            return Response(
                {"task_id": task.task_id}, status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "task_id",
                openapi.IN_QUERY,
                description="Id of task to generate report",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    @action(
        methods=["get"],
        detail=False,
        permission_classes=(IsAuthenticated,),
        filter_backends=None,
        pagination_class=None,
    )
    def get_report(self, request, *args, **kwargs):
        """Generate forecast report."""
        task_id = request.query_params.get("task_id", None)
        file_result = get_object_or_404(
            AsyncFileResults,
            task_id=task_id,
            user_id=request.user.id,
        )
        if not file_result.successful:
            return Response(**json.loads(file_result.errors))
        return FileResponse(
            file_result.result,
            as_attachment=True,
            status=status.HTTP_200_OK,
        )

    @action(methods=["get"], detail=False)
    def get_statistics(self, request):
        """Retrieve statistics based on forecast and sales data."""
        try:
            return Response(
                get_statistics_data(request).to_dict(orient="records"),
            )
        except Exception as e:
            return Response(
                {"error": {str(e)}},
                status=getattr(
                    e, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )


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
