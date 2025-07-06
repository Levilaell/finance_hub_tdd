import pytest
from django.db import IntegrityError
from apps.banking.models import BankProvider


class TestBankProviderModel:
    """Test suite for BankProvider model"""

    @pytest.mark.django_db
    def test_create_bank_provider(self):
        """Should create a bank provider with required fields"""
        provider = BankProvider.objects.create(
            name="Banco do Brasil",
            code="001",
            pluggy_connector_id="bb-connector-id",
            is_active=True,
            supports_checking_account=True,
            supports_savings_account=True,
            supports_credit_card=True,
        )

        assert provider.name == "Banco do Brasil"
        assert provider.code == "001"
        assert provider.pluggy_connector_id == "bb-connector-id"
        assert provider.is_active is True
        assert provider.supports_checking_account is True
        assert provider.supports_savings_account is True
        assert provider.supports_credit_card is True
        assert provider.created_at is not None
        assert provider.updated_at is not None

    @pytest.mark.django_db
    def test_bank_provider_str_representation(self):
        """Should return name as string representation"""
        provider = BankProvider.objects.create(
            name="Itaú",
            code="341",
            pluggy_connector_id="itau-connector-id",
        )

        assert str(provider) == "Itaú"

    @pytest.mark.django_db
    def test_bank_provider_unique_code(self):
        """Should enforce unique bank code constraint"""
        BankProvider.objects.create(
            name="Bradesco",
            code="237",
            pluggy_connector_id="bradesco-connector-id",
        )

        with pytest.raises(IntegrityError):
            BankProvider.objects.create(
                name="Bradesco Duplicate",
                code="237",  # Same code
                pluggy_connector_id="bradesco-duplicate-connector-id",
            )

    @pytest.mark.django_db
    def test_bank_provider_unique_pluggy_connector_id(self):
        """Should enforce unique pluggy connector id constraint"""
        BankProvider.objects.create(
            name="Santander",
            code="033",
            pluggy_connector_id="santander-connector-id",
        )

        with pytest.raises(IntegrityError):
            BankProvider.objects.create(
                name="Santander Duplicate",
                code="034",
                pluggy_connector_id="santander-connector-id",  # Same connector id
            )

    @pytest.mark.django_db
    def test_bank_provider_default_values(self):
        """Should set default values correctly"""
        provider = BankProvider.objects.create(
            name="Caixa",
            code="104",
            pluggy_connector_id="caixa-connector-id",
        )

        assert provider.is_active is True
        assert provider.supports_checking_account is True
        assert provider.supports_savings_account is True
        assert provider.supports_credit_card is False

    @pytest.mark.django_db
    def test_bank_provider_logo_url_optional(self):
        """Should allow logo_url to be optional"""
        provider = BankProvider.objects.create(
            name="Nubank",
            code="260",
            pluggy_connector_id="nubank-connector-id",
            logo_url="https://example.com/nubank-logo.png",
        )

        assert provider.logo_url == "https://example.com/nubank-logo.png"

        provider_without_logo = BankProvider.objects.create(
            name="Inter",
            code="077",
            pluggy_connector_id="inter-connector-id",
        )

        assert provider_without_logo.logo_url == ""

    @pytest.mark.django_db
    def test_bank_provider_ordering(self):
        """Should order bank providers by name"""
        BankProvider.objects.create(
            name="Bradesco",
            code="237",
            pluggy_connector_id="bradesco-connector-id",
        )
        BankProvider.objects.create(
            name="Banco do Brasil",
            code="001",
            pluggy_connector_id="bb-connector-id",
        )
        BankProvider.objects.create(
            name="Caixa",
            code="104",
            pluggy_connector_id="caixa-connector-id",
        )

        providers = BankProvider.objects.all()
        names = [p.name for p in providers]

        assert names == ["Banco do Brasil", "Bradesco", "Caixa"]

    @pytest.mark.django_db
    def test_get_active_providers(self):
        """Should filter only active providers"""
        active_provider = BankProvider.objects.create(
            name="Banco Ativo",
            code="999",
            pluggy_connector_id="active-connector-id",
            is_active=True,
        )
        inactive_provider = BankProvider.objects.create(
            name="Banco Inativo",
            code="998",
            pluggy_connector_id="inactive-connector-id",
            is_active=False,
        )

        active_providers = BankProvider.objects.filter(is_active=True)

        assert active_provider in active_providers
        assert inactive_provider not in active_providers
        assert active_providers.count() == 1