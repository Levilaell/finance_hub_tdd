import django_filters
from django.db import models
from .models import Transaction


class TransactionFilter(django_filters.FilterSet):
    """Filter for Transaction model"""

    date_from = django_filters.DateFilter(
        field_name="transaction_date", lookup_expr="gte"
    )
    date_to = django_filters.DateFilter(
        field_name="transaction_date", lookup_expr="lte"
    )
    amount_min = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount_max = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = Transaction
        fields = {
            "bank_account": ["exact"],
            "transaction_type": ["exact"],
            "is_pending": ["exact"],
            "category": ["exact", "icontains"],
            "subcategory": ["exact", "icontains"],
        }