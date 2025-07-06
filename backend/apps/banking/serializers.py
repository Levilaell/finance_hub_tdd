from rest_framework import serializers
from .models import BankProvider, BankAccount, Transaction


class BankProviderSerializer(serializers.ModelSerializer):
    """Serializer for BankProvider model"""

    class Meta:
        model = BankProvider
        fields = [
            "id",
            "name",
            "code",
            "pluggy_connector_id",
            "logo_url",
            "is_active",
            "supports_checking_account",
            "supports_savings_account",
            "supports_credit_card",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BankAccountSerializer(serializers.ModelSerializer):
    """Serializer for BankAccount model with nested provider"""

    bank_provider = BankProviderSerializer(read_only=True)
    transactions_count = serializers.SerializerMethodField()

    class Meta:
        model = BankAccount
        fields = [
            "id",
            "company",
            "bank_provider",
            "pluggy_item_id",
            "pluggy_account_id",
            "account_type",
            "name",
            "agency",
            "account_number",
            "balance",
            "is_active",
            "last_sync",
            "transactions_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "transactions_count"]

    def get_transactions_count(self, obj):
        """Get the number of transactions for this account"""
        return obj.transactions.count()


class BankAccountCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating BankAccount"""

    class Meta:
        model = BankAccount
        fields = [
            "company",
            "bank_provider",
            "pluggy_item_id",
            "pluggy_account_id",
            "account_type",
            "name",
            "agency",
            "account_number",
            "balance",
            "is_active",
        ]

    def validate_pluggy_account_id(self, value):
        """Validate that pluggy_account_id is unique"""
        if BankAccount.objects.filter(pluggy_account_id=value).exists():
            raise serializers.ValidationError(
                "A bank account with this Pluggy account ID already exists."
            )
        return value


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""

    bank_account_details = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "bank_account",
            "bank_account_details",
            "pluggy_transaction_id",
            "transaction_type",
            "amount",
            "description",
            "transaction_date",
            "posted_date",
            "category",
            "subcategory",
            "is_pending",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "bank_account_details"]

    def get_bank_account_details(self, obj):
        """Get basic bank account details for the transaction"""
        return {
            "name": obj.bank_account.name,
            "bank_provider_name": obj.bank_account.bank_provider.name,
            "account_type": obj.bank_account.account_type,
        }