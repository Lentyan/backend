from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from api.v1 import views

schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version="v1",
        description="Description",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

v1_router = DefaultRouter()
v1_router.register(r"skus", views.SKUViewSet, basename="skus")
v1_router.register(r"groups", views.GroupViewSet, basename="groups")
v1_router.register(r"categories", views.CategoryViewSet, basename="categories")
v1_router.register(
    r"subcategories", views.SubcategoryViewSet, basename="subcategories"
)
v1_router.register(r"shops", views.StoreViewSet, basename="shops")
v1_router.register(r"sales", views.SaleViewSet, basename="sales")
v1_router.register(r"forecasts", views.ForecastViewSet, basename="forecasts")
v1_router.register(r"user", views.UserViewSet, basename="user")

urlpatterns = [
    path("", include(v1_router.urls)),
    path("generate_report/", views.GenerateForecastReport.as_view()),
    path("auth/", include("djoser.urls.jwt")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
