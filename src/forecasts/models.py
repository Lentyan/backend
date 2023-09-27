import pytz
from django.db import models
from django.utils.translation import gettext_lazy as _


class Store(models.Model):
    """Model representing stores information."""

    class LocChoices(models.Choices):
        """Store loc field choices."""

        FIRST = 1
        SECOND = 2
        THIRD = 3

    class TypeFormatChoices(models.Choices):
        """Store type format choices."""

        FIRST = 1
        SECOND = 2
        THIRD = 3
        FOURTH = 4

    store = models.CharField(
        max_length=255,
        verbose_name="Магазин",
    )
    city = models.CharField(
        max_length=255,
        verbose_name="Населенный пункт",
    )
    division = models.CharField(
        max_length=256,
        verbose_name="Дивизион",
    )
    type_format = models.IntegerField(
        verbose_name="Формат магазина",
        choices=TypeFormatChoices.choices,
    )
    loc = models.IntegerField(
        verbose_name="Локация/окружение магазина",
        choices=LocChoices.choices,
    )
    size = models.IntegerField(
        verbose_name="Размер магазина",
    )
    is_active = models.BooleanField(verbose_name="Активен")

    timezone = models.CharField(
        max_length=63,
        verbose_name="Часовой пояс",
        choices=[(tz, tz) for tz in pytz.all_timezones],
        default="UTC",
    )

    class Meta:
        """Store model metadata."""

        verbose_name = _(
            "Магазин",
        )
        verbose_name_plural = _(
            "Магазины",
        )
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "store",
                    "city",
                    "division",
                    "type_format",
                    "loc",
                    "size",
                ),
                name="unique_stores",
            )
        ]
        indexes = [
            models.Index(
                fields=(
                    "store",
                    "city",
                    "division",
                    "type_format",
                    "loc",
                    "size",
                )
            ),
        ]

    def __str__(self):
        """Return capitalized store name."""
        return self.store.capitalize()


class SKU(models.Model):
    """Model representing SKUs information."""

    class UOMChoices(models.Choices):
        """SKU uom field choices."""

        BY_WEIGHT = 17
        BY_PIECE = 1

    group = models.CharField(
        max_length=255,
        verbose_name="Группа",
    )
    category = models.CharField(
        max_length=255,
        verbose_name="Категория",
    )
    subcategory = models.CharField(
        max_length=256,
        verbose_name="Подкатегория",
    )
    sku = models.CharField(
        max_length=256,
        verbose_name="СКЮ",
    )
    uom = models.IntegerField(
        verbose_name="Единицы измерения",
        choices=UOMChoices.choices,
    )

    class Meta:
        """SKU model metadata."""

        verbose_name = _(
            "Товар",
        )
        verbose_name_plural = _(
            "Товары",
        )
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "group",
                    "category",
                    "subcategory",
                    "sku",
                    "uom",
                ),
                name="unique_SKUs",
            )
        ]
        indexes = [
            models.Index(
                fields=(
                    "group",
                    "category",
                    "subcategory",
                    "sku",
                    "uom",
                )
            ),
        ]

    def __str__(self):
        """Return capitalized SKU name."""
        return self.sku.capitalize()


class Sale(models.Model):
    """Model representing sales information."""

    store = models.ForeignKey(
        Store,
        related_name="store_sales",
        on_delete=models.DO_NOTHING,
        verbose_name="Магазин",
    )
    sku = models.ForeignKey(
        SKU,
        related_name="sku_sales",
        on_delete=models.DO_NOTHING,
        verbose_name="Товар",
    )
    date = models.DateTimeField(verbose_name="Дата продажи")
    sales_type = models.BooleanField(verbose_name="Наличие промо")
    sales_units = models.IntegerField(
        verbose_name="Число проданных товаров без промо",
    )
    sales_units_promo = models.IntegerField(
        verbose_name="Число проданных товаров c промо",
    )
    sales_rub = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма продаж без промо в рублях",
    )
    sales_rub_promo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма продаж c промо в рублях",
    )

    def __str__(self):
        """Return sales data as str."""
        return f"{self.sku} sale in {self.store} at {self.date}"

    class Meta:
        """Sale model meta data."""

        verbose_name = _(
            "Продажа",
        )
        verbose_name_plural = _(
            "Продажи",
        )
        ordering = ("id",)

        constraints = [
            models.UniqueConstraint(
                fields=(
                    "store",
                    "sku",
                    "date",
                ),
                name="unique_sales",
            )
        ]

        indexes = [
            models.Index(
                fields=(
                    "store",
                    "sku",
                    "date",
                )
            ),
        ]


class Forecast(models.Model):
    """Model representing forecasts information."""

    store = models.ForeignKey(
        Store,
        related_name="store_forecasts",
        on_delete=models.DO_NOTHING,
        verbose_name="Магазин",
    )
    sku = models.ForeignKey(
        SKU,
        related_name="sku_forecasts",
        on_delete=models.DO_NOTHING,
        verbose_name="Товар",
    )

    forecast_date = models.DateTimeField(
        verbose_name="Дата прогноза",
    )
    forecast = models.JSONField(
        verbose_name="Прогноз",
    )

    def __str__(self):
        """Return forecast data as str."""
        return (
            f"{self.sku} forecast for " f"{self.store} at {self.forecast_date}"
        )

    class Meta:
        """Forecast model meta data."""

        verbose_name = _(
            "Прогноз",
        )
        verbose_name_plural = _(
            "Прогнозы",
        )
        ordering = ("id",)

        constraints = [
            models.UniqueConstraint(
                fields=(
                    "store",
                    "sku",
                    "forecast_date",
                ),
                name="unique_forecasts",
            )
        ]
        indexes = [
            models.Index(
                fields=(
                    "store",
                    "sku",
                    "forecast_date",
                )
            ),
        ]
