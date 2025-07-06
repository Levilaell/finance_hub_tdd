import pytest
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.companies.models import Company
from apps.reports.models import Report, ScheduledReport

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


@pytest.fixture
def report_template(company, user):
    """Criar um relatório template para agendamento"""
    return Report.objects.create(
        company=company,
        name='Template DRE Mensal',
        report_type='dre',
        parameters={
            'start_date': '{{start_date}}',
            'end_date': '{{end_date}}',
            'accounts': ['all']
        },
        format='pdf',
        created_by=user,
        status='completed'
    )


@pytest.mark.django_db
class TestScheduledReportModel:
    """Testes para o modelo ScheduledReport"""

    def test_create_scheduled_report(self, report_template):
        """Deve criar relatório agendado"""
        scheduled = ScheduledReport.objects.create(
            report_template=report_template,
            frequency='monthly',
            recipients=['user1@example.com', 'user2@example.com'],
            day_of_month=1,
            time_of_day='08:00'
        )

        assert scheduled.report_template == report_template
        assert scheduled.frequency == 'monthly'
        assert scheduled.recipients == ['user1@example.com', 'user2@example.com']
        assert scheduled.is_active is True
        assert scheduled.day_of_month == 1
        assert scheduled.time_of_day == '08:00'

    def test_frequency_choices(self, report_template):
        """Deve validar frequências suportadas"""
        frequencies = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']
        
        for frequency in frequencies:
            scheduled = ScheduledReport.objects.create(
                report_template=report_template,
                frequency=frequency,
                recipients=['test@example.com']
            )
            assert scheduled.frequency == frequency

    def test_calculate_next_run_daily(self, report_template):
        """Deve calcular próxima execução para frequência diária"""
        scheduled = ScheduledReport.objects.create(
            report_template=report_template,
            frequency='daily',
            recipients=['test@example.com'],
            time_of_day='14:30'
        )

        # Definir última execução como ontem
        scheduled.last_run = timezone.now() - timedelta(days=1)
        scheduled.save()

        next_run = scheduled.calculate_next_run()
        now = timezone.now()
        
        # Deve ser hoje ou amanhã às 14:30, dependendo da hora atual
        if now.hour < 14 or (now.hour == 14 and now.minute < 30):
            assert next_run.date() == now.date()
        else:
            assert next_run.date() == (now + timedelta(days=1)).date()
        assert next_run.hour == 14
        assert next_run.minute == 30

    def test_calculate_next_run_weekly(self, report_template):
        """Deve calcular próxima execução para frequência semanal"""
        scheduled = ScheduledReport.objects.create(
            report_template=report_template,
            frequency='weekly',
            recipients=['test@example.com'],
            day_of_week=1,  # Segunda-feira
            time_of_day='09:00'
        )

        next_run = scheduled.calculate_next_run()
        
        # Deve ser a próxima segunda-feira às 09:00
        assert next_run.weekday() == 0  # 0 = segunda-feira
        assert next_run.hour == 9
        assert next_run.minute == 0

    def test_calculate_next_run_monthly(self, report_template):
        """Deve calcular próxima execução para frequência mensal"""
        scheduled = ScheduledReport.objects.create(
            report_template=report_template,
            frequency='monthly',
            recipients=['test@example.com'],
            day_of_month=15,
            time_of_day='10:00'
        )

        next_run = scheduled.calculate_next_run()
        
        # Deve ser dia 15 do mês atual ou próximo
        assert next_run.day == 15
        assert next_run.hour == 10
        assert next_run.minute == 0

    def test_is_due_for_execution(self, report_template):
        """Deve verificar se está na hora de executar"""
        scheduled = ScheduledReport.objects.create(
            report_template=report_template,
            frequency='daily',
            recipients=['test@example.com'],
            time_of_day='14:00'
        )

        # Simular que next_run é agora
        scheduled.next_run = timezone.now() - timedelta(minutes=5)
        scheduled.save()

        assert scheduled.is_due_for_execution() is True

        # Simular que next_run é no futuro
        scheduled.next_run = timezone.now() + timedelta(hours=1)
        scheduled.save()

        assert scheduled.is_due_for_execution() is False

    def test_mark_as_executed(self, report_template):
        """Deve marcar como executado e calcular próxima execução"""
        scheduled = ScheduledReport.objects.create(
            report_template=report_template,
            frequency='daily',
            recipients=['test@example.com'],
            time_of_day='10:00'
        )

        old_next_run = scheduled.next_run
        scheduled.mark_as_executed()

        assert scheduled.last_run is not None
        assert scheduled.next_run >= old_next_run  # Pode ser igual se executado exatamente no horário
        assert scheduled.execution_count == 1

    def test_execution_count_tracking(self, report_template):
        """Deve rastrear quantidade de execuções"""
        scheduled = ScheduledReport.objects.create(
            report_template=report_template,
            frequency='daily',
            recipients=['test@example.com']
        )

        assert scheduled.execution_count == 0

        # Simular 3 execuções
        for i in range(3):
            scheduled.mark_as_executed()

        assert scheduled.execution_count == 3

    def test_deactivate_scheduled_report(self, report_template):
        """Deve permitir desativar relatório agendado"""
        scheduled = ScheduledReport.objects.create(
            report_template=report_template,
            frequency='daily',
            recipients=['test@example.com']
        )

        assert scheduled.is_active is True

        scheduled.deactivate()
        assert scheduled.is_active is False
        assert scheduled.deactivated_at is not None

    def test_reactivate_scheduled_report(self, report_template):
        """Deve permitir reativar relatório agendado"""
        scheduled = ScheduledReport.objects.create(
            report_template=report_template,
            frequency='daily',
            recipients=['test@example.com']
        )

        scheduled.deactivate()
        assert scheduled.is_active is False

        scheduled.reactivate()
        assert scheduled.is_active is True
        assert scheduled.next_run is not None

    def test_get_parameter_values(self, report_template):
        """Deve gerar valores de parâmetros baseado no período"""
        scheduled = ScheduledReport.objects.create(
            report_template=report_template,
            frequency='monthly',
            recipients=['test@example.com']
        )

        # Para relatório mensal
        params = scheduled.get_parameter_values()
        
        # Deve ter start_date e end_date do mês anterior
        assert 'start_date' in params
        assert 'end_date' in params
        assert params['accounts'] == ['all']

    def test_add_remove_recipients(self, report_template):
        """Deve permitir adicionar e remover destinatários"""
        scheduled = ScheduledReport.objects.create(
            report_template=report_template,
            frequency='daily',
            recipients=['user1@example.com']
        )

        # Adicionar destinatário
        scheduled.add_recipient('user2@example.com')
        assert 'user2@example.com' in scheduled.recipients
        assert len(scheduled.recipients) == 2

        # Remover destinatário
        scheduled.remove_recipient('user1@example.com')
        assert 'user1@example.com' not in scheduled.recipients
        assert len(scheduled.recipients) == 1

    def test_str_representation(self, report_template):
        """Deve ter representação em string adequada"""
        scheduled = ScheduledReport.objects.create(
            report_template=report_template,
            frequency='monthly',
            recipients=['test@example.com']
        )

        expected = f'{report_template.name} - Mensal'
        assert str(scheduled) == expected

    def test_quarterly_schedule(self, report_template):
        """Deve calcular próxima execução trimestral"""
        scheduled = ScheduledReport.objects.create(
            report_template=report_template,
            frequency='quarterly',
            recipients=['test@example.com'],
            quarter_months=[1, 4, 7, 10],  # Jan, Abr, Jul, Out
            day_of_month=5,
            time_of_day='09:00'
        )

        next_run = scheduled.calculate_next_run()
        
        # Deve ser no dia 5 de um dos meses do trimestre
        assert next_run.month in [1, 4, 7, 10]
        assert next_run.day == 5

    def test_yearly_schedule(self, report_template):
        """Deve calcular próxima execução anual"""
        scheduled = ScheduledReport.objects.create(
            report_template=report_template,
            frequency='yearly',
            recipients=['test@example.com'],
            month_of_year=12,  # Dezembro
            day_of_month=31,
            time_of_day='23:59'
        )

        next_run = scheduled.calculate_next_run()
        
        # Deve ser 31 de dezembro
        assert next_run.month == 12
        assert next_run.day == 31
        assert next_run.hour == 23
        assert next_run.minute == 59