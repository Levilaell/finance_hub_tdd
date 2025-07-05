# Guia Completo de Desenvolvimento TDD - Sistema de Gestão Financeira

## Índice

1. [Visão Geral do Sistema](#visão-geral-do-sistema)
2. [Especificações Técnicas Detalhadas](#especificações-técnicas-detalhadas)
3. [Arquitetura do Sistema](#arquitetura-do-sistema)
4. [Estrutura de Testes TDD](#estrutura-de-testes-tdd)
5. [Fluxos de Trabalho](#fluxos-de-trabalho)
6. [Requisitos de Frontend](#requisitos-de-frontend)
7. [Guia de Implementação Passo-a-Passo](#guia-de-implementação-passo-a-passo)

## 1. Visão Geral do Sistema

### Descrição
Sistema SaaS de gestão financeira completo para pequenas e médias empresas (PMEs) brasileiras, com integração bancária via Open Banking, categorização automática por IA, relatórios avançados e gestão multi-empresa.

### Objetivos Principais
- Centralizar informações financeiras de múltiplas contas bancárias
- Automatizar categorização de transações com IA (acredito que não seja necessário usar IA para isso, parece que os dados das transações via Pluggy já vem categorizados)
- Gerar relatórios e insights financeiros
- Facilitar controle orçamentário e metas financeiras
- Suportar múltiplas empresas com planos de assinatura

### Stack Tecnológico
- **Backend**: Django 5.0.1 + Django REST Framework
- **Frontend**: Next.js 14 + TypeScript + TailwindCSS
- **Banco de Dados**: PostgreSQL 15
- **Cache/Fila**: Redis 7 + Celery
- **Tempo Real**: Django Channels (WebSocket)
- **Containerização**: Docker + Docker Compose
- **Testes**: pytest (backend) + Jest/RTL (frontend)

## 2. Especificações Técnicas Detalhadas

### 2.1 Módulo de Autenticação e Usuários

#### Funcionalidades
1. **Registro de Usuário**
   - Campos obrigatórios: nome, email, senha, nome da empresa
   - Campos opcionais: telefone, data de nascimento
   - Criação automática de empresa no registro
   - Envio de email de verificação
   - Login automático após registro

2. **Autenticação JWT**
   - Token de acesso (15 minutos)
   - Token de refresh (7 dias)
   - Renovação automática de tokens
   - Logout com blacklist de tokens

3. **Autenticação Dois Fatores (2FA)**
   - Integração com Google Authenticator
   - Geração de QR Code
   - Códigos de backup (10 códigos)
   - Ativação/desativação por usuário

4. **Gestão de Perfil**
   - Atualização de dados pessoais
   - Upload de avatar
   - Preferências de idioma e fuso horário
   - Configurações de notificação

5. **Recuperação de Senha**
   - Envio de token por email
   - Validade de 1 hora
   - Link único de redefinição
   - Histórico de IPs de login

#### Modelos de Dados
```python
# User Model
- id: UUID
- email: EmailField (unique, username)
- first_name: CharField(150)
- last_name: CharField(150)
- phone: CharField(20, opcional)
- avatar: ImageField(opcional)
- date_of_birth: DateField(opcional)
- timezone: CharField(50, default='America/Sao_Paulo')
- language: CharField(10, default='pt-BR')
- is_active: BooleanField(default=True)
- is_staff: BooleanField(default=False)
- date_joined: DateTimeField(auto_now_add=True)
- last_login: DateTimeField(null=True)
- two_factor_enabled: BooleanField(default=False)
- two_factor_secret: CharField(32, encrypted)
- backup_codes: JSONField(encrypted)
- email_verified: BooleanField(default=False)
- email_verification_token: CharField(64)
- email_verification_sent_at: DateTimeField
- password_reset_token: CharField(64)
- password_reset_sent_at: DateTimeField
- last_login_ip: GenericIPAddressField
- customer_id: CharField(50) # payment gateway
- payment_gateway: CharField(20) # stripe/mercadopago
```

### 2.2 Módulo de Empresas e Assinaturas

#### Funcionalidades
1. **Gestão de Empresas**
   - Cadastro completo (CNPJ, razão social, tipo, setor)
   - Logo e cores personalizadas
   - Múltiplos endereços
   - Métricas de negócio (faturamento, funcionários)

2. **Planos de Assinatura**
   - **Starter**: R$ 29/mês
     - 2 contas bancárias
     - 1.000 transações/mês
     - 3 usuários
     - Relatórios básicos
   
   - **Pro**: R$ 79/mês
     - 10 contas bancárias
     - 10.000 transações/mês
     - 10 usuários
     - Todos os relatórios
     - Integração com contador
   
   - **Enterprise**: R$ 199/mês
     - Contas ilimitadas
     - Transações ilimitadas
     - Usuários ilimitados
     - API access
     - Suporte prioritário

3. **Gestão de Usuários da Empresa**
   - Convites por email
   - Papéis: Owner, Admin, Manager, Accountant, Viewer
   - Permissões granulares
   - Histórico de ações

4. **Trial e Billing**
   - Trial de 14 dias
   - Integração com Stripe e MercadoPago
   - Faturas mensais/anuais
   - Upgrade/downgrade de plano
   - Cancelamento com período de graça

#### Modelos de Dados
```python
# Company Model
- id: UUID
- name: CharField(200)
- legal_name: CharField(200)
- cnpj: CharField(18, unique)
- company_type: CharField(20) # MEI, ME, EPP, etc
- business_sector: CharField(50)
- logo: ImageField
- primary_color: CharField(7)
- secondary_color: CharField(7)
- website: URLField
- phone: CharField(20)
- email: EmailField
- address: JSONField
- employee_count: IntegerField
- annual_revenue: DecimalField
- created_at: DateTimeField
- updated_at: DateTimeField

# Subscription Model
- id: UUID
- company: ForeignKey(Company)
- plan: ForeignKey(SubscriptionPlan)
- status: CharField(20) # active, trial, cancelled, etc
- trial_ends_at: DateTimeField
- current_period_start: DateTimeField
- current_period_end: DateTimeField
- cancelled_at: DateTimeField
- customer_id: CharField(50) # payment gateway
- subscription_id: CharField(50) # payment gateway
```

### 2.3 Módulo de Integração Bancária

#### Funcionalidades
1. **Conexão de Contas**
   - Integração via Pluggy (bancos brasileiros)
   - Integração via Belvo (backup)
   - OAuth2 flow
   - Armazenamento seguro de credenciais
   - Múltiplas contas por empresa

2. **Sincronização de Dados**
   - Sync automático a cada 4 horas
   - Sync manual sob demanda
   - Importação de transações (90 dias)
   - Atualização de saldos
   - Detecção de duplicatas

3. **Gestão de Transações**
   - Tipos: débito, crédito, PIX, TED, DOC, boleto, cartão
   - Informações do beneficiário
   - Categorização automática
   - Tags e notas personalizadas
   - Status de revisão

4. **Orçamentos**
   - Orçamentos por categoria
   - Períodos: mensal, semanal, anual, customizado
   - Alertas de limite (50%, 80%, 100%)
   - Rollover de valores não utilizados
   - Comparação com períodos anteriores

5. **Metas Financeiras**
   - Tipos: poupança, redução de dívida, redução de gastos
   - Acompanhamento automático
   - Marcos e lembretes
   - Visualização de progresso

#### Modelos de Dados
```python
# BankAccount Model
- id: UUID
- company: ForeignKey(Company)
- provider: ForeignKey(BankProvider)
- name: CharField(200)
- account_type: CharField(20) # checking, savings, business
- account_number: CharField(20, encrypted)
- agency: CharField(10, encrypted)
- balance: DecimalField
- available_balance: DecimalField
- currency: CharField(3, default='BRL')
- status: CharField(20) # active, inactive, error
- integration_id: CharField(100) # Pluggy/Belvo ID
- credentials: JSONField(encrypted)
- last_sync: DateTimeField
- sync_enabled: BooleanField(default=True)

# Transaction Model
- id: UUID
- account: ForeignKey(BankAccount)
- external_id: CharField(100, unique)
- transaction_type: CharField(20)
- amount: DecimalField
- description: TextField
- merchant_name: CharField(200)
- merchant_category: CharField(50)
- category: ForeignKey(Category, null=True)
- ai_category: ForeignKey(Category, null=True)
- ai_confidence: FloatField
- date: DateField
- posted_date: DateField
- counterpart_name: CharField(200)
- counterpart_document: CharField(20)
- counterpart_bank: CharField(100)
- notes: TextField
- tags: ManyToManyField(Tag)
- is_reviewed: BooleanField(default=False)
- created_at: DateTimeField
```

### 2.4 Módulo de Categorização com IA

#### Funcionalidades
1. **Sistema de Categorias**
   - Categorias hierárquicas (pai/filho)
   - Tipos: receita, despesa, transferência
   - Ícones e cores personalizados
   - Categorias do sistema vs. usuário

2. **Categorização por IA**
   - Modelo de ML treinado
   - Score de confiança (0-100%)
   - Sugestões alternativas
   - Aprendizado com correções
   - Métricas de performance

3. **Regras de Categorização**
   - Regras por palavra-chave
   - Regras por valor
   - Regras por beneficiário
   - Expressões regulares
   - Prioridade de execução

4. **Analytics de Categorização**
   - Taxa de acerto
   - Categorias mais usadas
   - Evolução temporal
   - Relatórios de performance

#### Modelos de Dados
```python
# Category Model
- id: UUID
- company: ForeignKey(Company, null=True) # null = sistema
- name: CharField(100)
- parent: ForeignKey('self', null=True)
- category_type: CharField(20) # income, expense, transfer
- icon: CharField(50)
- color: CharField(7)
- is_system: BooleanField(default=False)
- created_at: DateTimeField

# CategorizationRule Model
- id: UUID
- company: ForeignKey(Company)
- name: CharField(100)
- rule_type: CharField(20) # keyword, amount, counterpart
- pattern: CharField(200)
- category: ForeignKey(Category)
- priority: IntegerField
- is_active: BooleanField(default=True)
```

### 2.5 Módulo de Relatórios

#### Funcionalidades
1. **Tipos de Relatórios**
   - DRE (Demonstração de Resultados)
   - Fluxo de Caixa
   - Análise por Categoria
   - Comparativo Mensal
   - Relatório Fiscal
   - Relatórios Customizados

2. **Formatos de Exportação**
   - PDF (com gráficos)
   - Excel (múltiplas abas)
   - CSV
   - JSON

3. **Agendamento**
   - Geração automática
   - Frequências: diária, semanal, mensal
   - Envio por email
   - Lista de distribuição

4. **Visualizações**
   - Gráficos de linha (tendências)
   - Gráficos de pizza (distribuição)
   - Gráficos de barra (comparativos)
   - Tabelas detalhadas

#### Modelos de Dados
```python
# Report Model
- id: UUID
- company: ForeignKey(Company)
- name: CharField(200)
- report_type: CharField(50)
- parameters: JSONField
- format: CharField(10)
- status: CharField(20) # pending, processing, completed, error
- file: FileField
- created_by: ForeignKey(User)
- created_at: DateTimeField

# ScheduledReport Model
- id: UUID
- report: ForeignKey(Report)
- frequency: CharField(20)
- next_run: DateTimeField
- recipients: JSONField
- is_active: BooleanField(default=True)
```

### 2.6 Módulo de Notificações

#### Funcionalidades
1. **Tipos de Notificações**
   - Saldo baixo
   - Transação alta
   - Orçamento excedido
   - Meta alcançada
   - Erro de sincronização
   - Relatório pronto
   - Assinatura expirando

2. **Canais de Entrega**
   - In-app (WebSocket)
   - Email
   - SMS (opcional)
   - Push (futuro)

3. **Configurações**
   - Preferências por tipo
   - Horário silencioso
   - Digest diário/semanal
   - Templates customizados

#### Modelos de Dados
```python
# Notification Model
- id: UUID
- user: ForeignKey(User)
- notification_type: CharField(50)
- title: CharField(200)
- message: TextField
- data: JSONField
- is_read: BooleanField(default=False)
- created_at: DateTimeField
- read_at: DateTimeField
```

### 2.7 Módulo de Pagamentos

#### Funcionalidades
1. **Gateways Suportados**
   - Stripe (internacional)
   - MercadoPago (Brasil/LATAM)

2. **Operações**
   - Criação de cliente
   - Gestão de assinaturas
   - Atualização de plano
   - Métodos de pagamento
   - Cancelamentos
   - Reembolsos

3. **Webhooks**
   - Pagamento aprovado
   - Pagamento falhou
   - Assinatura cancelada
   - Cartão expirado

#### Modelos de Dados
```python
# Payment Model
- id: UUID
- subscription: ForeignKey(Subscription)
- amount: DecimalField
- currency: CharField(3)
- status: CharField(20)
- payment_method: CharField(50)
- gateway: CharField(20)
- gateway_payment_id: CharField(100)
- paid_at: DateTimeField
- created_at: DateTimeField
```

## 3. Arquitetura do Sistema

### 3.1 Arquitetura Backend (Django)

#### Estrutura de Diretórios
```
backend/
├── apps/
│   ├── authentication/    # Autenticação e usuários
│   ├── companies/        # Empresas e assinaturas
│   ├── banking/         # Integração bancária
│   ├── categories/      # Categorização e IA
│   ├── reports/        # Relatórios
│   ├── notifications/  # Notificações
│   └── payments/      # Pagamentos
├── core/             # Configurações Django
├── utils/           # Utilidades compartilhadas
├── tests/          # Testes de integração
└── requirements/   # Dependências por ambiente
```

#### Padrões de Design
1. **Repository Pattern** para acesso a dados
2. **Service Layer** para lógica de negócio
3. **Serializers** para validação e transformação
4. **ViewSets** para APIs RESTful
5. **Permissions** para controle de acesso
6. **Signals** para eventos do sistema
7. **Celery Tasks** para processamento assíncrono

#### APIs e Endpoints
```
/api/auth/
    POST   /register/
    POST   /login/
    POST   /logout/
    POST   /refresh/
    POST   /verify-email/
    POST   /forgot-password/
    POST   /reset-password/
    GET    /profile/
    PUT    /profile/
    POST   /2fa/enable/
    POST   /2fa/disable/
    POST   /2fa/verify/

/api/companies/
    GET    /                    # Lista empresas do usuário
    POST   /                    # Cria empresa
    GET    /{id}/              # Detalhes da empresa
    PUT    /{id}/              # Atualiza empresa
    DELETE /{id}/              # Remove empresa
    GET    /{id}/users/        # Usuários da empresa
    POST   /{id}/invite/       # Convida usuário
    GET    /plans/             # Planos disponíveis
    POST   /{id}/subscribe/    # Assina plano
    POST   /{id}/cancel/       # Cancela assinatura

/api/banking/
    GET    /providers/          # Lista provedores
    GET    /accounts/          # Lista contas
    POST   /accounts/          # Conecta conta
    GET    /accounts/{id}/     # Detalhes da conta
    PUT    /accounts/{id}/     # Atualiza conta
    DELETE /accounts/{id}/     # Remove conta
    POST   /accounts/{id}/sync/ # Sincroniza conta
    GET    /transactions/      # Lista transações
    GET    /transactions/{id}/ # Detalhes da transação
    PUT    /transactions/{id}/ # Atualiza transação
    POST   /transactions/bulk/ # Operações em massa
    GET    /budgets/          # Lista orçamentos
    POST   /budgets/          # Cria orçamento
    GET    /goals/            # Lista metas
    POST   /goals/            # Cria meta

/api/categories/
    GET    /                   # Lista categorias
    POST   /                   # Cria categoria
    GET    /{id}/             # Detalhes da categoria
    PUT    /{id}/             # Atualiza categoria
    DELETE /{id}/             # Remove categoria
    GET    /rules/            # Lista regras
    POST   /rules/            # Cria regra
    POST   /categorize/       # Categoriza transações

/api/reports/
    GET    /                   # Lista relatórios
    POST   /                   # Gera relatório
    GET    /{id}/             # Download relatório
    GET    /scheduled/        # Lista agendados
    POST   /scheduled/        # Agenda relatório

/api/notifications/
    GET    /                   # Lista notificações
    PUT    /{id}/read/        # Marca como lida
    POST   /mark-all-read/    # Marca todas como lidas
    GET    /preferences/      # Preferências
    PUT    /preferences/      # Atualiza preferências
```

### 3.2 Arquitetura Frontend (Next.js)

#### Estrutura de Diretórios
```
frontend/
├── app/
│   ├── (auth)/           # Layout de autenticação
│   │   ├── login/
│   │   ├── register/
│   │   └── forgot-password/
│   └── (dashboard)/      # Layout do dashboard
│       ├── dashboard/
│       ├── accounts/
│       ├── transactions/
│       ├── categories/
│       ├── reports/
│       └── settings/
├── components/
│   ├── ui/              # Componentes base
│   ├── forms/           # Formulários
│   ├── charts/          # Gráficos
│   └── layout/          # Layout components
├── hooks/               # Custom hooks
├── services/           # Camada de API
├── store/             # Estado global
├── types/             # TypeScript types
└── utils/             # Utilidades
```

#### Padrões de Design
1. **Component Composition** para UI
2. **Custom Hooks** para lógica reutilizável
3. **Service Layer** para chamadas API
4. **Zustand** para estado global
5. **React Query** para cache de dados
6. **Zod** para validação de schemas
7. **React Hook Form** para formulários

### 3.3 Infraestrutura

#### Docker Compose Services
```yaml
services:
  postgres:    # Banco de dados principal
  redis:       # Cache e filas
  backend:     # API Django
  celery:      # Worker de tarefas
  celery-beat: # Agendador de tarefas
  frontend:    # Aplicação Next.js
  nginx:       # Proxy reverso
```

#### Variáveis de Ambiente
```
# Backend
DATABASE_URL=postgresql://user:pass@postgres:5432/financedb
REDIS_URL=redis://redis:6379/0
SECRET_KEY=django-secret-key
DEBUG=False
ALLOWED_HOSTS=api.financeapp.com
CORS_ALLOWED_ORIGINS=https://app.financeapp.com

# Integrações
PLUGGY_CLIENT_ID=xxx
PLUGGY_CLIENT_SECRET=xxx
BELVO_SECRET_ID=xxx
BELVO_SECRET_PASSWORD=xxx
STRIPE_SECRET_KEY=xxx
MERCADOPAGO_ACCESS_TOKEN=xxx

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@financeapp.com
EMAIL_HOST_PASSWORD=xxx

# Frontend
NEXT_PUBLIC_API_URL=https://api.financeapp.com
NEXT_PUBLIC_WEBSOCKET_URL=wss://api.financeapp.com/ws
```

## 4. Estrutura de Testes TDD

### 4.1 Filosofia TDD

#### Ciclo Red-Green-Refactor
1. **Red**: Escrever teste que falha
2. **Green**: Implementar código mínimo para passar
3. **Refactor**: Melhorar código mantendo testes verdes

#### Princípios
- Testar comportamento, não implementação
- Um teste por vez
- Testes devem ser independentes
- Testes devem ser rápidos
- Testes devem ser determinísticos

### 4.2 Estrutura de Testes Backend

#### Organização dos Testes
```
backend/
├── apps/
│   ├── authentication/
│   │   └── tests/
│   │       ├── test_models.py
│   │       ├── test_serializers.py
│   │       ├── test_views.py
│   │       ├── test_services.py
│   │       └── test_permissions.py
│   └── [outros apps com mesma estrutura]
└── tests/
    ├── integration/
    ├── fixtures/
    └── utils/
```

#### Exemplos de Testes por Módulo

##### Autenticação - Testes de Modelo
```python
# test_models.py
class TestUserModel:
    def test_create_user_with_email(self):
        """Deve criar usuário com email como username"""
        # Arrange
        email = "user@example.com"
        password = "SecurePass123!"
        
        # Act
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name="John",
            last_name="Doe"
        )
        
        # Assert
        assert user.email == email
        assert user.username == email
        assert user.check_password(password)
        assert user.is_active
        assert not user.is_staff
        assert not user.two_factor_enabled
    
    def test_create_superuser(self):
        """Deve criar superusuário com permissões admin"""
        # Test implementation...
    
    def test_user_full_name_property(self):
        """Deve retornar nome completo do usuário"""
        # Test implementation...
    
    def test_enable_two_factor_authentication(self):
        """Deve habilitar 2FA e gerar secret"""
        # Test implementation...
```

##### Autenticação - Testes de API
```python
# test_views.py
class TestAuthenticationAPI:
    def test_user_registration_success(self, api_client):
        """Deve registrar novo usuário e empresa"""
        # Arrange
        data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "Jane",
            "last_name": "Doe",
            "company_name": "Acme Corp",
            "company_cnpj": "11.222.333/0001-81"
        }
        
        # Act
        response = api_client.post("/api/auth/register/", data)
        
        # Assert
        assert response.status_code == 201
        assert "access" in response.data
        assert "refresh" in response.data
        assert User.objects.filter(email=data["email"]).exists()
        assert Company.objects.filter(cnpj=data["company_cnpj"]).exists()
    
    def test_login_with_valid_credentials(self, api_client):
        """Deve autenticar com credenciais válidas"""
        # Test implementation...
    
    def test_login_with_2fa_enabled(self, api_client, user_with_2fa):
        """Deve exigir código 2FA quando habilitado"""
        # Test implementation...
    
    def test_token_refresh(self, api_client, authenticated_user):
        """Deve renovar token de acesso"""
        # Test implementation...
```

##### Banking - Testes de Serviço
```python
# test_services.py
class TestBankingService:
    def test_connect_bank_account_pluggy(self, mock_pluggy_api):
        """Deve conectar conta bancária via Pluggy"""
        # Arrange
        mock_pluggy_api.create_item.return_value = {
            "id": "item_123",
            "status": "UPDATED"
        }
        service = BankingService()
        
        # Act
        account = service.connect_account(
            company_id="company_123",
            provider="pluggy",
            credentials={"user": "12345678", "password": "1234"}
        )
        
        # Assert
        assert account.integration_id == "item_123"
        assert account.status == "active"
        mock_pluggy_api.create_item.assert_called_once()
    
    def test_sync_transactions(self, mock_pluggy_api, bank_account):
        """Deve sincronizar transações da conta"""
        # Test implementation...
    
    def test_categorize_transaction_with_ai(self, mock_ai_service):
        """Deve categorizar transação usando IA"""
        # Test implementation...
    
    def test_apply_categorization_rules(self, company_with_rules):
        """Deve aplicar regras de categorização"""
        # Test implementation...
```

##### Reports - Testes de Geração
```python
# test_reports.py
class TestReportGeneration:
    def test_generate_monthly_dre_report(self, company_with_transactions):
        """Deve gerar relatório DRE mensal"""
        # Arrange
        report_service = ReportService()
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        # Act
        report = report_service.generate_dre(
            company=company_with_transactions,
            start_date=start_date,
            end_date=end_date
        )
        
        # Assert
        assert report.total_revenue == Decimal("10000.00")
        assert report.total_expenses == Decimal("7500.00")
        assert report.net_income == Decimal("2500.00")
        assert len(report.revenue_by_category) == 3
        assert len(report.expenses_by_category) == 5
    
    def test_export_report_to_pdf(self, generated_report):
        """Deve exportar relatório para PDF"""
        # Test implementation...
    
    def test_schedule_recurring_report(self, company):
        """Deve agendar relatório recorrente"""
        # Test implementation...
```

### 4.3 Estrutura de Testes Frontend

#### Organização dos Testes
```
frontend/
├── __tests__/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   └── services/
├── __mocks__/
│   ├── handlers/     # MSW handlers
│   └── data/        # Mock data
└── jest.config.js
```

#### Exemplos de Testes por Tipo

##### Testes de Componente
```typescript
// __tests__/components/TransactionTable.test.tsx
describe('TransactionTable', () => {
  it('should render transactions with correct formatting', () => {
    // Arrange
    const transactions = [
      {
        id: '1',
        description: 'Supermercado ABC',
        amount: -150.50,
        date: '2024-01-15',
        category: { name: 'Alimentação', icon: '🍕' }
      }
    ];
    
    // Act
    render(<TransactionTable transactions={transactions} />);
    
    // Assert
    expect(screen.getByText('Supermercado ABC')).toBeInTheDocument();
    expect(screen.getByText('-R$ 150,50')).toBeInTheDocument();
    expect(screen.getByText('15/01/2024')).toBeInTheDocument();
    expect(screen.getByText('🍕 Alimentação')).toBeInTheDocument();
  });
  
  it('should handle bulk selection', () => {
    // Test implementation...
  });
  
  it('should filter transactions by search term', () => {
    // Test implementation...
  });
});
```

##### Testes de Hook
```typescript
// __tests__/hooks/useAuth.test.ts
describe('useAuth', () => {
  it('should login user and store tokens', async () => {
    // Arrange
    const { result } = renderHook(() => useAuth());
    const credentials = {
      email: 'user@example.com',
      password: 'password123'
    };
    
    // Act
    await act(async () => {
      await result.current.login(credentials);
    });
    
    // Assert
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual({
      id: '123',
      email: 'user@example.com',
      name: 'John Doe'
    });
    expect(localStorage.getItem('access_token')).toBeTruthy();
  });
  
  it('should refresh token when expired', async () => {
    // Test implementation...
  });
  
  it('should logout and clear tokens', () => {
    // Test implementation...
  });
});
```

##### Testes de Integração
```typescript
// __tests__/pages/Dashboard.test.tsx
describe('Dashboard Page', () => {
  it('should load and display financial summary', async () => {
    // Arrange
    const user = userEvent.setup();
    
    // Act
    render(<Dashboard />);
    
    // Assert - Loading state
    expect(screen.getByText('Carregando...')).toBeInTheDocument();
    
    // Assert - Loaded state
    await waitFor(() => {
      expect(screen.getByText('Saldo Total')).toBeInTheDocument();
      expect(screen.getByText('R$ 15.430,50')).toBeInTheDocument();
      expect(screen.getByText('Receitas do Mês')).toBeInTheDocument();
      expect(screen.getByText('R$ 8.500,00')).toBeInTheDocument();
    });
  });
  
  it('should navigate to transactions on card click', async () => {
    // Test implementation...
  });
  
  it('should show real-time notifications', async () => {
    // Test implementation...
  });
});
```

### 4.4 Fixtures e Mocks

#### Backend Fixtures
```python
# fixtures/users.py
@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@example.com",
        password="TestPass123!",
        first_name="Test",
        last_name="User"
    )

@pytest.fixture
def user_with_2fa(user):
    user.enable_two_factor()
    return user

# fixtures/companies.py
@pytest.fixture
def company(user):
    return Company.objects.create(
        name="Test Company",
        cnpj="11.222.333/0001-81",
        owner=user
    )

@pytest.fixture
def company_with_pro_plan(company):
    plan = SubscriptionPlan.objects.get(name="Pro")
    Subscription.objects.create(
        company=company,
        plan=plan,
        status="active"
    )
    return company
```

#### Frontend Mocks
```typescript
// __mocks__/handlers/auth.ts
export const authHandlers = [
  rest.post('/api/auth/login/', (req, res, ctx) => {
    const { email, password } = req.body as LoginRequest;
    
    if (email === 'test@example.com' && password === 'password123') {
      return res(
        ctx.status(200),
        ctx.json({
          access: 'mock-access-token',
          refresh: 'mock-refresh-token',
          user: {
            id: '123',
            email: 'test@example.com',
            name: 'Test User'
          }
        })
      );
    }
    
    return res(
      ctx.status(401),
      ctx.json({ detail: 'Invalid credentials' })
    );
  })
];
```

## 5. Fluxos de Trabalho

### 5.1 Fluxo de Registro e Onboarding

```mermaid
1. Usuário acessa /register
2. Preenche formulário:
   - Dados pessoais (nome, email, senha)
   - Dados da empresa (nome, CNPJ)
3. Sistema valida:
   - Email único
   - CNPJ válido e único
   - Senha forte
4. Sistema cria:
   - Usuário com email não verificado
   - Empresa com trial de 14 dias
   - Tokens JWT
5. Envia email de verificação
6. Redireciona para dashboard com banner de verificação
7. Usuário verifica email
8. Sistema marca email como verificado
9. Exibe modal de onboarding:
   - Tour pelas funcionalidades
   - Sugestão de conectar primeira conta
```

### 5.2 Fluxo de Conexão Bancária

```mermaid
1. Usuário acessa /accounts
2. Clica em "Conectar Conta"
3. Seleciona banco da lista
4. Sistema inicia OAuth com Pluggy:
   - Redireciona para Pluggy Connect
   - Usuário faz login no banco
   - Autoriza acesso
5. Pluggy retorna para callback URL
6. Sistema:
   - Cria conta bancária
   - Salva tokens criptografados
   - Inicia primeira sincronização
7. Celery task:
   - Busca transações (90 dias)
   - Busca saldos
   - Categoriza com IA
8. WebSocket notifica progresso
9. Atualiza UI com dados sincronizados
```

### 5.3 Fluxo de Categorização Inteligente

```mermaid
1. Nova transação sincronizada
2. Sistema extrai features:
   - Descrição
   - Valor
   - Tipo
   - Merchant
3. Aplica regras customizadas:
   - Verifica match de keywords
   - Verifica ranges de valor
   - Verifica beneficiário
4. Se não houver match:
   - Envia para modelo de IA
   - Recebe categoria + confiança
5. Se confiança > 85%:
   - Aplica automaticamente
   - Marca como AI categorizado
6. Se confiança < 85%:
   - Marca para revisão
   - Sugere top 3 categorias
7. Usuário revisa/corrige
8. Sistema aprende com correção
```

### 5.4 Fluxo de Geração de Relatórios

```mermaid
1. Usuário acessa /reports
2. Seleciona tipo de relatório
3. Define parâmetros:
   - Período
   - Contas
   - Categorias
   - Formato
4. Clica em "Gerar"
5. Sistema cria job no Celery
6. Celery task:
   - Busca dados do período
   - Processa cálculos
   - Gera gráficos
   - Cria arquivo (PDF/Excel)
7. WebSocket notifica progresso
8. Salva em S3/local
9. Notifica conclusão
10. Usuário faz download
```

### 5.5 Fluxo de Gestão de Assinatura

```mermaid
1. Trial expirando (3 dias antes)
2. Sistema envia email de lembrete
3. Exibe banner no dashboard
4. Usuário acessa /settings/billing
5. Visualiza planos disponíveis
6. Seleciona plano desejado
7. Redireciona para gateway:
   - Stripe Checkout ou
   - MercadoPago Checkout
8. Usuário completa pagamento
9. Gateway envia webhook
10. Sistema:
    - Atualiza assinatura
    - Ativa features do plano
    - Envia email de confirmação
11. Remove banners de trial
```

## 6. Requisitos de Frontend

### 6.1 Design System

#### Cores
```css
/* Cores Principais */
--primary: #4F46E5;        /* Indigo-600 */
--primary-hover: #4338CA;  /* Indigo-700 */
--secondary: #7C3AED;      /* Violet-600 */
--accent: #EC4899;         /* Pink-500 */

/* Cores de Status */
--success: #10B981;        /* Green-500 */
--warning: #F59E0B;        /* Amber-500 */
--error: #EF4444;         /* Red-500 */
--info: #3B82F6;          /* Blue-500 */

/* Neutros */
--gray-50: #F9FAFB;
--gray-100: #F3F4F6;
--gray-200: #E5E7EB;
--gray-300: #D1D5DB;
--gray-400: #9CA3AF;
--gray-500: #6B7280;
--gray-600: #4B5563;
--gray-700: #374151;
--gray-800: #1F2937;
--gray-900: #111827;

/* Financeiro */
--income: #10B981;        /* Verde para receitas */
--expense: #EF4444;       /* Vermelho para despesas */
--neutral: #6B7280;       /* Cinza para neutro */
```

#### Tipografia
```css
/* Font Family */
--font-sans: 'Inter', system-ui, sans-serif;
--font-mono: 'JetBrains Mono', monospace;

/* Font Sizes */
--text-xs: 0.75rem;      /* 12px */
--text-sm: 0.875rem;     /* 14px */
--text-base: 1rem;       /* 16px */
--text-lg: 1.125rem;     /* 18px */
--text-xl: 1.25rem;      /* 20px */
--text-2xl: 1.5rem;      /* 24px */
--text-3xl: 1.875rem;    /* 30px */
--text-4xl: 2.25rem;     /* 36px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

#### Espaçamento
```css
/* Spacing Scale */
--space-1: 0.25rem;      /* 4px */
--space-2: 0.5rem;       /* 8px */
--space-3: 0.75rem;      /* 12px */
--space-4: 1rem;         /* 16px */
--space-5: 1.25rem;      /* 20px */
--space-6: 1.5rem;       /* 24px */
--space-8: 2rem;         /* 32px */
--space-10: 2.5rem;      /* 40px */
--space-12: 3rem;        /* 48px */
--space-16: 4rem;        /* 64px */
```

#### Componentes Base

##### Botões
```tsx
// Variantes
<Button variant="primary">Ação Principal</Button>
<Button variant="secondary">Ação Secundária</Button>
<Button variant="outline">Ação Outline</Button>
<Button variant="ghost">Ação Ghost</Button>
<Button variant="destructive">Ação Destrutiva</Button>

// Tamanhos
<Button size="sm">Pequeno</Button>
<Button size="md">Médio</Button>
<Button size="lg">Grande</Button>

// Estados
<Button disabled>Desabilitado</Button>
<Button loading>Carregando...</Button>
```

##### Cards
```tsx
<Card>
  <CardHeader>
    <CardTitle>Título do Card</CardTitle>
    <CardDescription>Descrição opcional</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Conteúdo */}
  </CardContent>
  <CardFooter>
    {/* Ações */}
  </CardFooter>
</Card>
```

##### Formulários
```tsx
<Form>
  <FormField>
    <FormLabel>Email</FormLabel>
    <FormControl>
      <Input type="email" placeholder="seu@email.com" />
    </FormControl>
    <FormMessage>Mensagem de erro</FormMessage>
  </FormField>
</Form>
```

### 6.2 Layouts Responsivos

#### Breakpoints
```css
--mobile: 640px;    /* sm */
--tablet: 768px;    /* md */
--laptop: 1024px;   /* lg */
--desktop: 1280px;  /* xl */
--wide: 1536px;     /* 2xl */
```

#### Grid System
```tsx
// Dashboard Grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  {/* Cards de métricas */}
</div>

// Transaction Table
<div className="w-full overflow-x-auto">
  <Table className="min-w-[768px]">
    {/* Tabela com scroll horizontal no mobile */}
  </Table>
</div>

// Sidebar Layout
<div className="flex h-screen">
  <Sidebar className="hidden lg:block w-64" />
  <MobileSidebar className="lg:hidden" />
  <main className="flex-1 overflow-y-auto">
    {/* Conteúdo principal */}
  </main>
</div>
```

### 6.3 Componentes Específicos

#### Gráficos Financeiros
```tsx
// Gráfico de Fluxo de Caixa
<AreaChart
  data={cashFlowData}
  lines={[
    { key: 'income', color: 'green', name: 'Receitas' },
    { key: 'expenses', color: 'red', name: 'Despesas' },
    { key: 'balance', color: 'blue', name: 'Saldo' }
  ]}
/>

// Gráfico de Pizza - Categorias
<PieChart
  data={categoryData}
  valueKey="amount"
  nameKey="category"
  colors={['#4F46E5', '#7C3AED', '#EC4899', '#F59E0B']}
/>

// Gráfico de Barras - Comparativo
<BarChart
  data={monthlyComparison}
  bars={[
    { key: 'lastYear', color: 'gray', name: 'Ano Anterior' },
    { key: 'thisYear', color: 'primary', name: 'Este Ano' }
  ]}
/>
```

#### Seletor de Conta Bancária
```tsx
<BankAccountSelector
  accounts={bankAccounts}
  selected={selectedAccount}
  onChange={setSelectedAccount}
  showBalance={true}
  showStatus={true}
/>
```

#### Seletor de Categoria com Ícone
```tsx
<CategorySelect
  value={category}
  onChange={setCategory}
  type="expense" // income, expense, all
  showIcon={true}
  allowCreate={true}
/>
```

#### Timeline de Transações
```tsx
<TransactionTimeline
  transactions={transactions}
  groupBy="day" // day, week, month
  showRunningBalance={true}
/>
```

### 6.4 Animações e Transições

```css
/* Transições Padrão */
--transition-fast: 150ms ease-in-out;
--transition-base: 200ms ease-in-out;
--transition-slow: 300ms ease-in-out;

/* Animações */
@keyframes slideIn {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

### 6.5 Estados de Loading e Empty

#### Loading States
```tsx
// Skeleton Loading
<div className="space-y-4">
  <Skeleton className="h-32 w-full" /> {/* Card */}
  <Skeleton className="h-10 w-3/4" />  {/* Title */}
  <Skeleton className="h-4 w-full" />   {/* Text */}
</div>

// Spinner Loading
<div className="flex items-center justify-center h-64">
  <Spinner size="lg" />
  <span className="ml-2">Carregando transações...</span>
</div>

// Progress Loading
<ProgressBar value={progress} max={100} />
```

#### Empty States
```tsx
<EmptyState
  icon={<BanknotesIcon />}
  title="Nenhuma transação encontrada"
  description="Conecte uma conta bancária para começar a importar suas transações"
  action={
    <Button onClick={connectAccount}>
      Conectar Conta
    </Button>
  }
/>
```

### 6.6 Acessibilidade

#### ARIA Labels
```tsx
<button
  aria-label="Sincronizar conta bancária"
  aria-pressed={isSyncing}
  aria-busy={isSyncing}
>
  <RefreshIcon aria-hidden="true" />
</button>
```

#### Navegação por Teclado
```tsx
// Atalhos de teclado
useKeyboardShortcuts({
  'cmd+k': () => openSearch(),
  'cmd+n': () => createTransaction(),
  'esc': () => closeModal()
});
```

#### Anúncios para Screen Readers
```tsx
<div className="sr-only" aria-live="polite" aria-atomic="true">
  {announcement}
</div>
```

## 7. Guia de Implementação Passo-a-Passo

### 7.1 Fase 1: Setup Inicial e Autenticação (Semana 1-2)

#### Dia 1-2: Setup do Projeto
```bash
# 1. Criar estrutura do projeto
mkdir finance-management && cd finance-management
mkdir backend frontend

# 2. Inicializar backend Django
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install django==5.0.1 djangorestframework pytest-django
django-admin startproject core .

# 3. Inicializar frontend Next.js
cd ../frontend
npx create-next-app@14 . --typescript --tailwind --app

# 4. Configurar Docker
cd ..
# Criar docker-compose.yml com todos os serviços
```

#### Dia 3-4: Modelo de Usuário Customizado

##### Testes Primeiro (TDD)
```python
# backend/apps/authentication/tests/test_models.py
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestUserModel:
    def test_create_user_with_email(self):
        """Deve criar usuário usando email como username"""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        assert user.email == 'test@example.com'
        assert user.username == 'test@example.com'
        assert user.check_password('TestPass123!')
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
```

##### Implementação
```python
# backend/apps/authentication/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)
```

#### Dia 5-6: API de Autenticação JWT

##### Testes da API
```python
# backend/apps/authentication/tests/test_views.py
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestAuthenticationAPI:
    def test_user_registration(self, api_client):
        """Deve registrar novo usuário via API"""
        data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = api_client.post('/api/auth/register/', data)
        
        assert response.status_code == 201
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert User.objects.filter(email=data['email']).exists()
```

##### Implementação das Views
```python
# backend/apps/authentication/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': serializer.data,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_201_CREATED)
```

#### Dia 7-8: Frontend - Páginas de Autenticação

##### Testes de Componentes
```typescript
// frontend/__tests__/pages/login.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Login from '@/app/(auth)/login/page'

describe('Login Page', () => {
  it('should login with valid credentials', async () => {
    const user = userEvent.setup()
    render(<Login />)
    
    // Preencher formulário
    await user.type(screen.getByLabelText(/email/i), 'user@example.com')
    await user.type(screen.getByLabelText(/senha/i), 'password123')
    
    // Submeter
    await user.click(screen.getByRole('button', { name: /entrar/i }))
    
    // Verificar redirecionamento
    await waitFor(() => {
      expect(window.location.pathname).toBe('/dashboard')
    })
  })
})
```

##### Implementação da Página
```tsx
// frontend/app/(auth)/login/page.tsx
'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(8, 'Senha deve ter no mínimo 8 caracteres')
})

type LoginData = z.infer<typeof loginSchema>

export default function Login() {
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuth()
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<LoginData>({
    resolver: zodResolver(loginSchema)
  })
  
  const onSubmit = async (data: LoginData) => {
    setIsLoading(true)
    try {
      await login(data)
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Input
        {...register('email')}
        type="email"
        placeholder="seu@email.com"
        error={errors.email?.message}
      />
      
      <Input
        {...register('password')}
        type="password"
        placeholder="Sua senha"
        error={errors.password?.message}
      />
      
      <Button type="submit" loading={isLoading} className="w-full">
        Entrar
      </Button>
    </form>
  )
}
```

### 7.2 Fase 2: Multi-tenancy e Empresas (Semana 3-4)

#### Dia 9-10: Modelo de Empresa

##### Testes do Modelo
```python
# backend/apps/companies/tests/test_models.py
@pytest.mark.django_db
class TestCompanyModel:
    def test_create_company_with_owner(self, user):
        """Deve criar empresa com dono"""
        company = Company.objects.create(
            name='Acme Corp',
            cnpj='11.222.333/0001-81',
            owner=user
        )
        
        assert company.name == 'Acme Corp'
        assert company.owner == user
        assert company.users.filter(id=user.id).exists()
        
    def test_user_can_have_multiple_companies(self, user):
        """Usuário pode ter múltiplas empresas"""
        company1 = Company.objects.create(
            name='Company 1',
            cnpj='11.111.111/0001-11',
            owner=user
        )
        company2 = Company.objects.create(
            name='Company 2', 
            cnpj='22.222.222/0001-22',
            owner=user
        )
        
        assert user.owned_companies.count() == 2
```

##### Implementação
```python
# backend/apps/companies/models.py
class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    legal_name = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, unique=True)
    owner = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        related_name='owned_companies'
    )
    users = models.ManyToManyField(
        User,
        through='CompanyUser',
        related_name='companies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Companies'

class CompanyUser(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['company', 'user']
```

#### Dia 11-12: Sistema de Assinaturas

##### Testes de Assinatura
```python
# backend/apps/companies/tests/test_subscriptions.py
@pytest.mark.django_db
class TestSubscription:
    def test_create_trial_subscription(self, company):
        """Deve criar assinatura trial ao criar empresa"""
        subscription = Subscription.objects.create_trial(company)
        
        assert subscription.status == 'trial'
        assert subscription.plan.name == 'Starter'
        assert subscription.trial_days_remaining > 0
        
    def test_upgrade_subscription(self, company_with_trial):
        """Deve fazer upgrade de plano"""
        pro_plan = SubscriptionPlan.objects.get(name='Pro')
        subscription = company_with_trial.subscription
        
        subscription.upgrade_to(pro_plan)
        
        assert subscription.plan == pro_plan
        assert subscription.status == 'active'
```

### 7.3 Fase 3: Integração Bancária (Semana 5-7)

#### Dia 13-15: Modelos e API de Contas

##### Testes de Conta Bancária
```python
# backend/apps/banking/tests/test_models.py
@pytest.mark.django_db
class TestBankAccount:
    def test_create_bank_account(self, company):
        """Deve criar conta bancária"""
        account = BankAccount.objects.create(
            company=company,
            provider_id='pluggy',
            name='Conta Corrente',
            account_type='checking',
            integration_id='item_123'
        )
        
        assert account.company == company
        assert account.is_active
        assert account.balance == Decimal('0.00')
        
    def test_encrypt_credentials(self, bank_account):
        """Deve criptografar credenciais"""
        credentials = {'token': 'secret123'}
        bank_account.set_credentials(credentials)
        bank_account.save()
        
        # Verificar que não está em plain text
        assert 'secret123' not in str(bank_account.credentials)
        
        # Verificar que consegue decriptar
        assert bank_account.get_credentials() == credentials
```

#### Dia 16-18: Integração com Pluggy

##### Testes de Integração
```python
# backend/apps/banking/tests/test_pluggy_integration.py
@pytest.mark.django_db
class TestPluggyIntegration:
    @patch('apps.banking.services.pluggy.PluggyClient')
    def test_connect_account(self, mock_pluggy, company):
        """Deve conectar conta via Pluggy"""
        # Mock da resposta
        mock_pluggy.return_value.create_item.return_value = {
            'id': 'item_123',
            'status': 'UPDATED',
            'connector': {'name': 'Banco do Brasil'}
        }
        
        service = BankingService()
        account = service.connect_account(
            company=company,
            connector_id='001',
            credentials={'user': '12345', 'password': '1234'}
        )
        
        assert account.integration_id == 'item_123'
        assert account.provider.name == 'Banco do Brasil'
```

##### Implementação do Serviço
```python
# backend/apps/banking/services/banking_service.py
class BankingService:
    def __init__(self):
        self.pluggy = PluggyClient()
        
    def connect_account(self, company, connector_id, credentials):
        # Criar item no Pluggy
        item = self.pluggy.create_item(
            connector_id=connector_id,
            credentials=credentials
        )
        
        # Criar conta no sistema
        provider = BankProvider.objects.get(
            pluggy_connector_id=connector_id
        )
        
        account = BankAccount.objects.create(
            company=company,
            provider=provider,
            integration_id=item['id'],
            name=f"{provider.name} - Conta",
            status='pending'
        )
        
        # Iniciar sincronização
        sync_bank_account.delay(account.id)
        
        return account
```

#### Dia 19-21: Sincronização de Transações

##### Testes de Sincronização
```python
# backend/apps/banking/tests/test_sync.py
@pytest.mark.django_db
class TestTransactionSync:
    @patch('apps.banking.services.pluggy.PluggyClient')
    def test_sync_transactions(self, mock_pluggy, bank_account):
        """Deve sincronizar transações da conta"""
        # Mock das transações
        mock_pluggy.return_value.get_transactions.return_value = [
            {
                'id': 'tx_1',
                'description': 'Supermercado XYZ',
                'amount': -150.50,
                'date': '2024-01-15',
                'type': 'DEBIT'
            },
            {
                'id': 'tx_2',
                'description': 'Salário',
                'amount': 5000.00,
                'date': '2024-01-05',
                'type': 'CREDIT'
            }
        ]
        
        service = BankingService()
        transactions = service.sync_transactions(bank_account)
        
        assert len(transactions) == 2
        assert Transaction.objects.filter(
            account=bank_account
        ).count() == 2
        
        # Verificar categorização automática
        salary = Transaction.objects.get(external_id='tx_2')
        assert salary.ai_category is not None
        assert salary.ai_category.name == 'Salário'
```

### 7.4 Fase 4: Sistema de Categorização (Semana 8-9)

#### Dia 22-24: Categorização por Regras

##### Testes de Regras
```python
# backend/apps/categories/tests/test_rules.py
@pytest.mark.django_db
class TestCategorizationRules:
    def test_keyword_rule(self, company, expense_category):
        """Deve categorizar por palavra-chave"""
        rule = CategorizationRule.objects.create(
            company=company,
            name='Supermercados',
            rule_type='keyword',
            pattern='supermercado|mercado',
            category=expense_category
        )
        
        transaction = Transaction(
            description='Supermercado Pão de Açúcar',
            amount=-200.00
        )
        
        matched_category = rule.match(transaction)
        assert matched_category == expense_category
        
    def test_amount_range_rule(self, company, salary_category):
        """Deve categorizar por faixa de valor"""
        rule = CategorizationRule.objects.create(
            company=company,
            name='Salário',
            rule_type='amount',
            pattern='3000-10000',
            category=salary_category
        )
        
        transaction = Transaction(
            description='Pagamento',
            amount=5000.00
        )
        
        matched_category = rule.match(transaction)
        assert matched_category == salary_category
```

#### Dia 25-27: Integração com IA

##### Testes de IA
```python
# backend/apps/categories/tests/test_ai_categorization.py
@pytest.mark.django_db
class TestAICategorization:
    @patch('apps.categories.services.ai.predict_category')
    def test_ai_categorization(self, mock_predict, transaction):
        """Deve categorizar usando IA"""
        mock_predict.return_value = {
            'category_id': 'cat_123',
            'confidence': 0.92,
            'alternatives': [
                {'category_id': 'cat_456', 'confidence': 0.05}
            ]
        }
        
        service = AICategorizationService()
        result = service.categorize(transaction)
        
        assert result.category.id == 'cat_123'
        assert result.confidence == 0.92
        assert transaction.ai_category == result.category
        assert transaction.ai_confidence == 0.92
```

### 7.5 Fase 5: Dashboard e Visualizações (Semana 10-11)

#### Dia 28-30: Dashboard Principal

##### Testes do Dashboard
```typescript
// frontend/__tests__/pages/dashboard.test.tsx
describe('Dashboard', () => {
  it('should display financial summary', async () => {
    render(<Dashboard />)
    
    // Aguardar carregamento
    await waitFor(() => {
      expect(screen.getByText('Saldo Total')).toBeInTheDocument()
    })
    
    // Verificar métricas
    expect(screen.getByText('R$ 15.430,50')).toBeInTheDocument()
    expect(screen.getByText('Receitas do Mês')).toBeInTheDocument()
    expect(screen.getByText('R$ 8.500,00')).toBeInTheDocument()
    expect(screen.getByText('↑ 12.5%')).toBeInTheDocument()
  })
  
  it('should show recent transactions', async () => {
    render(<Dashboard />)
    
    await waitFor(() => {
      expect(screen.getByText('Transações Recentes')).toBeInTheDocument()
    })
    
    // Verificar lista de transações
    expect(screen.getByText('Supermercado ABC')).toBeInTheDocument()
    expect(screen.getByText('-R$ 150,50')).toBeInTheDocument()
  })
})
```

##### Implementação do Dashboard
```tsx
// frontend/app/(dashboard)/dashboard/page.tsx
export default function Dashboard() {
  const { data: summary, isLoading } = useQuery({
    queryKey: ['financial-summary'],
    queryFn: () => dashboardService.getSummary()
  })
  
  const { data: transactions } = useQuery({
    queryKey: ['recent-transactions'],
    queryFn: () => transactionService.getRecent()
  })
  
  if (isLoading) {
    return <DashboardSkeleton />
  }
  
  return (
    <div className="space-y-6">
      {/* Métricas principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Saldo Total"
          value={summary.totalBalance}
          change={summary.balanceChange}
          icon={<WalletIcon />}
        />
        <MetricCard
          title="Receitas do Mês"
          value={summary.monthlyIncome}
          change={summary.incomeChange}
          trend="up"
          icon={<ArrowUpIcon />}
        />
        {/* ... outras métricas */}
      </div>
      
      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Fluxo de Caixa</CardTitle>
          </CardHeader>
          <CardContent>
            <CashFlowChart data={summary.cashFlow} />
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Gastos por Categoria</CardTitle>
          </CardHeader>
          <CardContent>
            <CategoryPieChart data={summary.categoryBreakdown} />
          </CardContent>
        </Card>
      </div>
      
      {/* Transações recentes */}
      <Card>
        <CardHeader>
          <CardTitle>Transações Recentes</CardTitle>
          <Link href="/transactions" className="text-sm">
            Ver todas →
          </Link>
        </CardHeader>
        <CardContent>
          <TransactionList transactions={transactions} />
        </CardContent>
      </Card>
    </div>
  )
}
```

### 7.6 Fase 6: Relatórios e Insights (Semana 12-13)

#### Dia 31-33: Geração de Relatórios

##### Testes de Relatórios
```python
# backend/apps/reports/tests/test_report_generation.py
@pytest.mark.django_db
class TestReportGeneration:
    def test_generate_monthly_dre(self, company_with_transactions):
        """Deve gerar DRE mensal"""
        generator = DREReportGenerator()
        report = generator.generate(
            company=company_with_transactions,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        
        assert report.total_revenue == Decimal('10000.00')
        assert report.total_expenses == Decimal('7500.00')
        assert report.gross_profit == Decimal('2500.00')
        assert report.net_profit == Decimal('2500.00')
        
        # Verificar quebra por categoria
        assert 'Vendas' in report.revenue_breakdown
        assert 'Aluguel' in report.expense_breakdown
        
    def test_export_report_to_pdf(self, generated_report):
        """Deve exportar relatório para PDF"""
        exporter = PDFExporter()
        pdf_file = exporter.export(generated_report)
        
        assert pdf_file.exists()
        assert pdf_file.size > 0
        assert pdf_file.content_type == 'application/pdf'
```

### 7.7 Fase 7: Notificações e Real-time (Semana 14)

#### Dia 34-36: Sistema de Notificações

##### Testes de Notificações
```python
# backend/apps/notifications/tests/test_notifications.py
@pytest.mark.django_db
class TestNotifications:
    def test_low_balance_notification(self, user, bank_account):
        """Deve criar notificação de saldo baixo"""
        bank_account.balance = Decimal('100.00')
        bank_account.save()
        
        service = NotificationService()
        notification = service.check_low_balance(bank_account)
        
        assert notification is not None
        assert notification.type == 'low_balance'
        assert notification.user == user
        assert 'saldo baixo' in notification.message.lower()
        
    @patch('apps.notifications.tasks.send_email')
    def test_email_notification(self, mock_send_email, notification):
        """Deve enviar notificação por email"""
        service = NotificationService()
        service.send_email_notification(notification)
        
        mock_send_email.delay.assert_called_once()
        call_args = mock_send_email.delay.call_args[0]
        assert notification.user.email in call_args
```

#### Dia 37-38: WebSocket para Real-time

##### Testes WebSocket
```python
# backend/apps/notifications/tests/test_websocket.py
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_websocket_notifications():
    """Deve enviar notificações via WebSocket"""
    communicator = WebsocketCommunicator(
        application,
        "/ws/notifications/"
    )
    
    connected, _ = await communicator.connect()
    assert connected
    
    # Simular notificação
    await sync_to_async(Notification.objects.create)(
        user_id='user_123',
        type='transaction_sync',
        message='Sincronização concluída'
    )
    
    # Receber mensagem
    message = await communicator.receive_json_from()
    assert message['type'] == 'notification'
    assert message['data']['type'] == 'transaction_sync'
    
    await communicator.disconnect()
```

### 7.8 Fase 8: Finalização e Deploy (Semana 15-16)

#### Dia 39-40: Testes de Integração E2E

##### Cypress para E2E
```typescript
// cypress/e2e/complete-flow.cy.ts
describe('Complete User Flow', () => {
  it('should complete full financial management flow', () => {
    // 1. Registro
    cy.visit('/register')
    cy.fillRegistrationForm({
      email: 'test@example.com',
      password: 'SecurePass123!',
      company: 'Test Company',
      cnpj: '11.222.333/0001-81'
    })
    cy.submitForm()
    
    // 2. Verificar email (mock)
    cy.verifyEmail()
    
    // 3. Conectar conta bancária
    cy.visit('/accounts')
    cy.contains('Conectar Conta').click()
    cy.selectBank('Banco do Brasil')
    cy.fillBankCredentials()
    cy.wait('@bankSync')
    
    // 4. Verificar transações
    cy.visit('/transactions')
    cy.get('[data-testid="transaction-row"]').should('have.length.greaterThan', 0)
    
    // 5. Categorizar transação
    cy.get('[data-testid="transaction-row"]').first().click()
    cy.selectCategory('Alimentação')
    cy.contains('Salvar').click()
    
    // 6. Gerar relatório
    cy.visit('/reports')
    cy.selectReportType('DRE')
    cy.selectDateRange('Este Mês')
    cy.contains('Gerar').click()
    cy.wait('@reportGeneration')
    cy.contains('Download').should('be.visible')
  })
})
```

#### Dia 41-42: Performance e Otimização

##### Testes de Performance
```python
# backend/tests/performance/test_load.py
import pytest
from locust import HttpUser, task, between

class FinanceUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/auth/login/", {
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()["access"]
        self.client.headers.update({
            "Authorization": f"Bearer {self.token}"
        })
    
    @task(3)
    def view_dashboard(self):
        self.client.get("/api/dashboard/summary/")
    
    @task(2)
    def view_transactions(self):
        self.client.get("/api/banking/transactions/")
    
    @task(1)
    def sync_account(self):
        self.client.post("/api/banking/accounts/1/sync/")
```

## Considerações Finais

### Checklist de Implementação

#### Backend
- [ ] Setup inicial com Docker
- [ ] Modelo de usuário customizado
- [ ] Autenticação JWT
- [ ] Sistema de empresas/multi-tenancy
- [ ] Planos e assinaturas
- [ ] Integração bancária (Pluggy/Belvo)
- [ ] Sincronização de transações
- [ ] Categorização (regras + IA)
- [ ] Geração de relatórios
- [ ] Sistema de notificações
- [ ] WebSocket para real-time
- [ ] Tarefas assíncronas (Celery)
- [ ] Testes unitários (>80% coverage)
- [ ] Testes de integração
- [ ] Documentação da API

#### Frontend
- [ ] Setup Next.js 14 com TypeScript
- [ ] Sistema de autenticação
- [ ] Layout responsivo
- [ ] Dashboard com métricas
- [ ] Gestão de contas bancárias
- [ ] Lista de transações
- [ ] Sistema de categorias
- [ ] Geração de relatórios
- [ ] Gráficos e visualizações
- [ ] Notificações real-time
- [ ] Testes de componentes
- [ ] Testes E2E
- [ ] Otimização de performance

#### DevOps
- [ ] Docker compose completo
- [ ] CI/CD pipeline
- [ ] Monitoramento (Sentry)
- [ ] Logs centralizados
- [ ] Backup automatizado
- [ ] SSL/HTTPS
- [ ] Rate limiting
- [ ] Segurança (headers, CORS)

### Dicas de Implementação TDD

1. **Sempre escreva o teste primeiro**
   - Pense no comportamento desejado
   - Escreva teste que falha
   - Implemente o mínimo necessário

2. **Um teste por vez**
   - Não escreva vários testes de uma vez
   - Foque em fazer um teste passar
   - Refatore após verde

3. **Mantenha testes simples**
   - Teste uma coisa por vez
   - Use nomes descritivos
   - Arrange-Act-Assert

4. **Use fixtures e factories**
   - Crie dados de teste reutilizáveis
   - Mantenha testes independentes
   - Limpe dados após cada teste

5. **Mock dependências externas**
   - APIs de terceiros
   - Serviços de email
   - Sistemas de arquivos

6. **Teste casos extremos**
   - Valores nulos/vazios
   - Limites de validação
   - Erros de rede
   - Concorrência

Este guia fornece uma base sólida para recriar o sistema completo usando TDD. Cada fase build incrementalmente sobre a anterior, garantindo que o sistema seja robusto, testável e mantenível.