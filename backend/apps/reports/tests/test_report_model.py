import pytest
from decimal import Decimal
from datetime import datetime, date
from django.contrib.auth import get_user_model
from apps.companies.models import Company
from apps.reports.models import Report

User = get_user_model()


@pytest.fixture
def user(db):
    """Criar usuário de teste"""
    return User.objects.create_user(
        email='test@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def company(user):
    """Criar empresa de teste"""
    return Company.objects.create(
        name='Test Company',
        cnpj='11.222.333/0001-81',
        owner=user
    )


@pytest.mark.django_db
class TestReportModel:
    """Testes para o modelo Report"""

    def test_create_report(self, company, user):
        """Deve criar relatório com dados básicos"""
        report = Report.objects.create(
            company=company,
            name='Relatório DRE Janeiro 2024',
            report_type='dre',
            parameters={
                'start_date': '2024-01-01',
                'end_date': '2024-01-31',
                'accounts': ['all']
            },
            format='pdf',
            created_by=user
        )

        assert report.company == company
        assert report.name == 'Relatório DRE Janeiro 2024'
        assert report.report_type == 'dre'
        assert report.parameters['start_date'] == '2024-01-01'
        assert report.format == 'pdf'
        assert report.status == 'pending'
        assert report.created_by == user
        assert report.created_at is not None

    def test_report_types(self, company, user):
        """Deve validar tipos de relatório suportados"""
        report_types = ['dre', 'cashflow', 'category_analysis', 'monthly_comparison', 'fiscal', 'custom']
        
        for report_type in report_types:
            report = Report.objects.create(
                company=company,
                name=f'Relatório {report_type}',
                report_type=report_type,
                parameters={},
                format='pdf',
                created_by=user
            )
            assert report.report_type == report_type

    def test_report_formats(self, company, user):
        """Deve validar formatos de exportação suportados"""
        formats = ['pdf', 'excel', 'csv', 'json']
        
        for format_type in formats:
            report = Report.objects.create(
                company=company,
                name=f'Relatório {format_type}',
                report_type='dre',
                parameters={},
                format=format_type,
                created_by=user
            )
            assert report.format == format_type

    def test_report_status_transitions(self, company, user):
        """Deve gerenciar transições de status do relatório"""
        report = Report.objects.create(
            company=company,
            name='Relatório de Teste',
            report_type='dre',
            parameters={},
            format='pdf',
            created_by=user
        )

        # Status inicial deve ser pending
        assert report.status == 'pending'

        # Marcar como processando
        report.mark_as_processing()
        assert report.status == 'processing'
        assert report.processing_started_at is not None

        # Marcar como completo
        report.mark_as_completed(file_path='/reports/test.pdf')
        assert report.status == 'completed'
        assert report.completed_at is not None
        assert report.file_path == '/reports/test.pdf'

        # Marcar como erro
        report_error = Report.objects.create(
            company=company,
            name='Relatório com Erro',
            report_type='dre',
            parameters={},
            format='pdf',
            created_by=user
        )
        report_error.mark_as_error('Erro ao processar dados')
        assert report_error.status == 'error'
        assert report_error.error_message == 'Erro ao processar dados'

    def test_report_with_metadata(self, company, user):
        """Deve armazenar metadados do relatório"""
        report = Report.objects.create(
            company=company,
            name='Relatório com Metadados',
            report_type='dre',
            parameters={
                'start_date': '2024-01-01',
                'end_date': '2024-01-31',
            },
            format='pdf',
            created_by=user
        )

        # Adicionar metadados após processamento
        report.metadata = {
            'total_revenue': '10000.00',
            'total_expenses': '7500.00',
            'net_income': '2500.00',
            'transaction_count': 150,
            'categories_used': 12
        }
        report.save()

        assert report.metadata['total_revenue'] == '10000.00'
        assert report.metadata['transaction_count'] == 150

    def test_report_file_size_tracking(self, company, user):
        """Deve rastrear tamanho do arquivo gerado"""
        report = Report.objects.create(
            company=company,
            name='Relatório Grande',
            report_type='cashflow',
            parameters={},
            format='excel',
            created_by=user
        )

        # Simular conclusão com arquivo
        report.mark_as_completed(
            file_path='/reports/cashflow.xlsx',
            file_size=2048576  # 2MB
        )

        assert report.file_size == 2048576
        assert report.get_file_size_display() == '2.0 MB'

    def test_report_processing_time(self, company, user):
        """Deve calcular tempo de processamento"""
        report = Report.objects.create(
            company=company,
            name='Relatório Rápido',
            report_type='dre',
            parameters={},
            format='pdf',
            created_by=user
        )

        # Simular processamento
        report.mark_as_processing()
        import time
        time.sleep(0.1)  # Simular processamento
        report.mark_as_completed(file_path='/reports/quick.pdf')

        assert report.processing_time_seconds > 0
        assert report.processing_time_seconds < 1

    def test_report_str_representation(self, company, user):
        """Deve ter representação em string adequada"""
        report = Report.objects.create(
            company=company,
            name='DRE Janeiro 2024',
            report_type='dre',
            parameters={},
            format='pdf',
            created_by=user
        )

        assert str(report) == 'DRE Janeiro 2024 - Test Company'

    def test_report_ordering(self, company, user):
        """Deve ordenar relatórios por data de criação (mais recentes primeiro)"""
        report1 = Report.objects.create(
            company=company,
            name='Relatório 1',
            report_type='dre',
            parameters={},
            format='pdf',
            created_by=user
        )

        report2 = Report.objects.create(
            company=company,
            name='Relatório 2',
            report_type='dre',
            parameters={},
            format='pdf',
            created_by=user
        )

        reports = Report.objects.all()
        assert reports[0] == report2  # Mais recente primeiro
        assert reports[1] == report1

    def test_report_can_be_regenerated(self, company, user):
        """Deve permitir regeneração de relatório"""
        report = Report.objects.create(
            company=company,
            name='Relatório para Regenerar',
            report_type='dre',
            parameters={},
            format='pdf',
            created_by=user
        )

        # Completar relatório
        report.mark_as_completed(file_path='/reports/old.pdf')
        
        # Verificar se pode ser regenerado
        assert report.can_be_regenerated() is True

        # Marcar para regeneração
        report.mark_for_regeneration()
        assert report.status == 'pending'
        assert report.file_path is None
        assert report.completed_at is None