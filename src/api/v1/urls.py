from rest_framework.routers import DefaultRouter

from api.v1 import views

v1_router = DefaultRouter()
v1_router.register(r"categories", views.SKUViewSet, basename="categories")
v1_router.register(r"shops", views.StoreViewSet, basename="shops")
v1_router.register(r"sales", views.SaleViewSet, basename="sales")
v1_router.register(r"forecasts", views.ForecastViewSet, basename="forecasts")
