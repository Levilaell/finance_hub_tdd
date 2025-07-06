from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

User = get_user_model()


class Report(models.Model):
    """Modelo para relatórios gerados"""
    
    REPORT_TYPE_CHOICES = [
        ('dre', 'Demonstração de Resultado'),
        ('cashflow', 'Fluxo de Caixa'),
        ('category_analysis', 'Análise por Categoria'),
        ('monthly_comparison', 'Comparativo Mensal'),
        ('fiscal', 'Relatório Fiscal'),
        ('custom', 'Relatório Customizado'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('error', 'Erro'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='reports'
    )
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    parameters = models.JSONField(default=dict)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Arquivo gerado
    file_path = models.CharField(max_length=500, null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    
    # Metadados do relatório
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Erro (se houver)
    error_message = models.TextField(blank=True, default='')
    
    # Usuário que criou
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reports'
    )
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f'{self.name} - {self.company.name}'
    
    def mark_as_processing(self):
        """Marcar relatório como em processamento"""
        self.status = 'processing'
        self.processing_started_at = timezone.now()
        self.save(update_fields=['status', 'processing_started_at'])
    
    def mark_as_completed(self, file_path, file_size=None):
        """Marcar relatório como concluído"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.file_path = file_path
        if file_size:
            self.file_size = file_size
        self.save(update_fields=['status', 'completed_at', 'file_path', 'file_size'])
    
    def mark_as_error(self, error_message):
        """Marcar relatório com erro"""
        self.status = 'error'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message'])
    
    def get_file_size_display(self):
        """Retornar tamanho do arquivo formatado"""
        if not self.file_size:
            return '0 B'
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f'{size:.1f} {unit}'
            size /= 1024.0
        return f'{size:.1f} TB'
    
    @property
    def processing_time_seconds(self):
        """Calcular tempo de processamento em segundos"""
        if self.processing_started_at and self.completed_at:
            delta = self.completed_at - self.processing_started_at
            return delta.total_seconds()
        return 0
    
    def can_be_regenerated(self):
        """Verificar se relatório pode ser regenerado"""
        return self.status in ['completed', 'error']
    
    def mark_for_regeneration(self):
        """Marcar relatório para regeneração"""
        self.status = 'pending'
        self.file_path = None
        self.completed_at = None
        self.processing_started_at = None
        self.error_message = ''
        self.save(update_fields=[
            'status', 'file_path', 'completed_at', 
            'processing_started_at', 'error_message'
        ])


class ScheduledReport(models.Model):
    """Modelo para relatórios agendados"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_template = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    
    # Configurações de horário
    time_of_day = models.CharField(max_length=5, default='08:00')  # HH:MM
    day_of_week = models.IntegerField(null=True, blank=True)  # 1-7 (Mon-Sun)
    day_of_month = models.IntegerField(null=True, blank=True)  # 1-31
    month_of_year = models.IntegerField(null=True, blank=True)  # 1-12
    quarter_months = models.JSONField(default=list, blank=True)  # [1,4,7,10]
    
    # Destinatários
    recipients = models.JSONField(default=list)
    
    # Controle
    is_active = models.BooleanField(default=True)
    next_run = models.DateTimeField(null=True, blank=True)
    last_run = models.DateTimeField(null=True, blank=True)
    execution_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['next_run']
        
    def __str__(self):
        return f'{self.report_template.name} - {self.get_frequency_display()}'
    
    def save(self, *args, **kwargs):
        """Calcular next_run ao salvar"""
        if not self.next_run and self.is_active:
            self.next_run = self.calculate_next_run()
        super().save(*args, **kwargs)
    
    def calculate_next_run(self):
        """Calcular próxima execução baseado na frequência"""
        now = timezone.now()
        time_parts = self.time_of_day.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        
        if self.frequency == 'daily':
            # Próxima execução hoje ou amanhã no horário especificado
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run
            
        elif self.frequency == 'weekly':
            # Próxima execução no dia da semana especificado
            if self.day_of_week is None:
                self.day_of_week = 1  # Default para segunda-feira
            days_ahead = (self.day_of_week - 1 - now.weekday()) % 7
            if days_ahead == 0 and now.time() > datetime.strptime(self.time_of_day, '%H:%M').time():
                days_ahead = 7
            next_run = now + timedelta(days=days_ahead)
            return next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
        elif self.frequency == 'monthly':
            # Próxima execução no dia do mês especificado
            if self.day_of_month is None:
                self.day_of_month = 1  # Default para primeiro dia do mês
            next_run = now.replace(day=self.day_of_month, hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                # Avançar para o próximo mês
                if now.month == 12:
                    next_run = next_run.replace(year=now.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=now.month + 1)
            return next_run
            
        elif self.frequency == 'quarterly':
            # Próxima execução em um dos meses do trimestre
            current_month = now.month
            quarter_months = self.quarter_months or [1, 4, 7, 10]
            if self.day_of_month is None:
                self.day_of_month = 1
            
            # Encontrar próximo mês do trimestre
            next_month = None
            for month in sorted(quarter_months):
                if month > current_month or (month == current_month and now.day < self.day_of_month):
                    next_month = month
                    break
            
            if not next_month:
                next_month = quarter_months[0]
                year = now.year + 1
            else:
                year = now.year
                
            return datetime(
                year, next_month, self.day_of_month,
                hour, minute, tzinfo=now.tzinfo
            )
            
        elif self.frequency == 'yearly':
            # Próxima execução no mês e dia especificados
            if self.month_of_year is None:
                self.month_of_year = 1
            if self.day_of_month is None:
                self.day_of_month = 1
            next_run = now.replace(
                month=self.month_of_year,
                day=self.day_of_month,
                hour=hour, minute=minute, second=0, microsecond=0
            )
            if next_run <= now:
                next_run = next_run.replace(year=now.year + 1)
            return next_run
            
        return now + timedelta(days=1)  # Fallback
    
    def is_due_for_execution(self):
        """Verificar se está na hora de executar"""
        if not self.is_active or not self.next_run:
            return False
        return timezone.now() >= self.next_run
    
    def mark_as_executed(self):
        """Marcar como executado e calcular próxima execução"""
        self.last_run = timezone.now()
        self.execution_count += 1
        self.next_run = self.calculate_next_run()
        self.save(update_fields=['last_run', 'execution_count', 'next_run'])
    
    def get_parameter_values(self):
        """Gerar valores de parâmetros para o período atual"""
        params = self.report_template.parameters.copy()
        now = timezone.now()
        
        if self.frequency == 'monthly':
            # Pegar mês anterior
            if now.month == 1:
                start_date = date(now.year - 1, 12, 1)
            else:
                start_date = date(now.year, now.month - 1, 1)
            
            # Último dia do mês
            if start_date.month == 12:
                end_date = date(start_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(start_date.year, start_date.month + 1, 1) - timedelta(days=1)
                
            params['start_date'] = start_date.isoformat()
            params['end_date'] = end_date.isoformat()
            
        # Adicionar lógica para outras frequências conforme necessário
        
        return params
    
    def deactivate(self):
        """Desativar relatório agendado"""
        self.is_active = False
        self.deactivated_at = timezone.now()
        self.save(update_fields=['is_active', 'deactivated_at'])
    
    def reactivate(self):
        """Reativar relatório agendado"""
        self.is_active = True
        self.deactivated_at = None
        self.next_run = self.calculate_next_run()
        self.save(update_fields=['is_active', 'deactivated_at', 'next_run'])
    
    def add_recipient(self, email):
        """Adicionar destinatário"""
        if email not in self.recipients:
            self.recipients.append(email)
            self.save(update_fields=['recipients'])
    
    def remove_recipient(self, email):
        """Remover destinatário"""
        if email in self.recipients:
            self.recipients.remove(email)
            self.save(update_fields=['recipients'])
