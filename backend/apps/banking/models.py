from django.db import models
from apps.companies.models import Company


class BankProvider(models.Model):
    """Bank provider model for integration with Pluggy"""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    pluggy_connector_id = models.CharField(max_length=100, unique=True)
    logo_url = models.URLField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    supports_checking_account = models.BooleanField(default=True)
    supports_savings_account = models.BooleanField(default=True)
    supports_credit_card = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        db_table = "bank_providers"

    def __str__(self):
        return self.name


class BankAccount(models.Model):
    """Bank account model linked to company and provider"""

    ACCOUNT_TYPE_CHOICES = [
        ("CHECKING", "Conta Corrente"),
        ("SAVINGS", "Conta Poupança"),
        ("CREDIT_CARD", "Cartão de Crédito"),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="bank_accounts"
    )
    bank_provider = models.ForeignKey(
        BankProvider, on_delete=models.PROTECT, related_name="accounts"
    )
    pluggy_item_id = models.CharField(max_length=100)
    pluggy_account_id = models.CharField(max_length=100, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    agency = models.CharField(max_length=20, blank=True, default="")
    account_number = models.CharField(max_length=50, blank=True, default="")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "bank_accounts"

    def __str__(self):
        return f"{self.name} - {self.bank_provider.name}"


class Transaction(models.Model):
    """Transaction model for bank account movements"""

    TRANSACTION_TYPE_CHOICES = [
        ("DEBIT", "Débito"),
        ("CREDIT", "Crédito"),
    ]

    bank_account = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, related_name="transactions"
    )
    pluggy_transaction_id = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=500)
    transaction_date = models.DateField()
    posted_date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=100, blank=True, default="")
    subcategory = models.CharField(max_length=100, blank=True, default="")
    is_pending = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-transaction_date", "-created_at"]
        db_table = "transactions"
        unique_together = [["bank_account", "pluggy_transaction_id"]]

    def __str__(self):
        return f"{self.transaction_date} - R$ {self.amount} - {self.description}"
