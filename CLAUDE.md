# CLAUDE.md

Este arquivo fornece contexto completo ao Claude Code para desenvolvimento TDD do Sistema de Gestão Financeira.

## Projeto Overview

**Sistema SaaS de Gestão Financeira** para PMEs brasileiras com integração bancária via Open Banking, categorização automática, relatórios avançados e gestão multi-empresa.

**Metodologia**: Test-Driven Development (TDD) - RED → GREEN → REFACTOR

## 📊 STATUS ATUAL DO PROJETO

### ✅ Módulos Completos (Backend + Frontend)
- **Authentication**: Usuários, JWT, autenticação completa
- **Companies**: Multi-tenancy, assinaturas, permissões completas  
- **Categories**: Sistema hierárquico, regras automáticas, rule engine, frontend completo
- **Banking**: Models, Services, API, Tasks, Frontend completo

### 🔄 Módulos Parcialmente Implementados
- **Reports**: Models (Report, ScheduledReport) ✅, Services/Views ⏳

### ⏳ Módulos Pendentes  
- **Notifications**: Real-time, WebSocket
- **Payments**: Stripe, MercadoPago, billing

### 🎯 Próximo Foco
**Fase 5.1 Concluída!** Modelos Report e ScheduledReport implementados com TDD (25 testes passando). Próximos passos: Report Services e Views.

## Stack Tecnológico

### Backend
- **Django 5.0.1** + Django REST Framework
- **PostgreSQL 15** (banco principal)
- **Redis 7** (cache e filas)
- **Celery** (tarefas assíncronas)
- **Django Channels** (WebSocket)
- **pytest** + **pytest-django** (testes)

### Frontend
- **Next.js 14** + TypeScript + App Router
- **TailwindCSS** (styling)
- **Zustand** (estado global)
- **React Query** (cache de dados)
- **React Hook Form** + **Zod** (formulários)
- **Jest** + **React Testing Library** (testes)

### Containerização
- **Docker** + **Docker Compose**
- **nginx** (proxy reverso)

## Comandos de Desenvolvimento

### Setup Inicial
```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Instalar dependências backend
pip install -r requirements/local.txt

# Instalar dependências frontend
cd frontend && npm install --legacy-peer-deps

# Subir com Docker
docker-compose up -d
```

### Backend (Django)
```bash
# Rodar testes
pytest -v
pytest apps/authentication/tests/test_models.py::TestUserModel::test_create_user_with_email

# Rodar servidor
python manage.py runserver

# Migrações
python manage.py makemigrations
python manage.py migrate

# Shell Django
python manage.py shell

# Criar superuser
python manage.py createsuperuser

# Verificar código
black .
isort .
flake8 . --max-line-length=120 --exclude=migrations,venv
```

### Frontend (Next.js)
```bash
# Rodar testes
npm test
npm run test:watch

# Rodar desenvolvimento
npm run dev

# Build produção
npm run build

# Lint
npm run lint
```

### Celery
```bash
# Worker
celery -A core worker -l info

# Beat (scheduler)
celery -A core beat -l info

# Flower (monitor)
celery -A core flower
```

## Arquitetura do Sistema

### Estrutura Backend
```
backend/
├── apps/
│   ├── authentication/    # Usuários e autenticação
│   ├── companies/        # Empresas e assinaturas
│   ├── banking/         # Contas e transações
│   ├── categories/      # Categorização
│   ├── reports/        # Relatórios
│   ├── notifications/  # Notificações
│   └── payments/      # Pagamentos
├── core/             # Settings Django
├── utils/           # Utilitários
└── tests/          # Testes integração
```

### Estrutura Frontend
```
frontend/
├── app/
│   ├── (auth)/          # Páginas autenticação
│   └── (dashboard)/     # Dashboard protegido
├── components/
│   ├── ui/             # Componentes base
│   ├── forms/          # Formulários
│   └── charts/         # Gráficos
├── hooks/              # Custom hooks
├── services/           # Camada API
├── store/             # Estado global
└── __tests__/         # Testes
```

## Metodologia TDD

### Ciclo RED-GREEN-REFACTOR

#### 1. RED - Escrever Teste que Falha
```python
# Exemplo: test_user_creation
def test_create_user_with_email():
    """Deve criar usuário com email como username"""
    user = User.objects.create_user(
        email='test@example.com',
        password='SecurePass123!',
        first_name='Test',
        last_name='User'
    )
    assert user.email == 'test@example.com'
    assert user.username == 'test@example.com'
    assert user.is_active
```

#### 2. GREEN - Implementar Código Mínimo
```python
# Implementar apenas o suficiente para o teste passar
class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)
```

#### 3. REFACTOR - Melhorar Código
```python
# Refatorar mantendo testes verdes
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
```

### Padrões de Teste

#### Estrutura AAA (Arrange-Act-Assert)
```python
def test_example():
    # Arrange - Preparar dados
    user = User.objects.create_user(email='test@example.com')
    
    # Act - Executar ação
    result = user.get_full_name()
    
    # Assert - Verificar resultado
    assert result == 'Test User'
```

#### Fixtures para Reutilização
```python
@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='test@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='User'
    )

@pytest.fixture
def company(user):
    return Company.objects.create(
        name='Test Company',
        cnpj='11.222.333/0001-81',
        owner=user
    )
```

#### Mocks para Dependências Externas
```python
@patch('apps.banking.services.pluggy.PluggyClient')
def test_connect_bank_account(mock_pluggy, company):
    mock_pluggy.return_value.create_item.return_value = {
        'id': 'item_123',
        'status': 'UPDATED'
    }
    
    service = BankingService()
    account = service.connect_account(company, 'connector_id', {})
    
    assert account.integration_id == 'item_123'
    mock_pluggy.return_value.create_item.assert_called_once()
```

## Módulos do Sistema

### 1. Authentication (apps.authentication)
**Funcionalidades:**
- Modelo User customizado (email como username)
- JWT authentication (access + refresh tokens)
- Two-factor authentication (2FA)
- Password reset flow
- Email verification

**Testes Prioritários:**
- Criação de usuário
- Login/logout
- Token refresh
- 2FA enable/disable
- Password reset

### 2. Companies (apps.companies)
**Funcionalidades:**
- Multi-tenancy por empresa
- Planos de assinatura (Starter, Pro, Enterprise)
- Gestão de usuários da empresa
- Billing e pagamentos

**Testes Prioritários:**
- Criação de empresa
- Associação usuário-empresa
- Upgrade/downgrade plano
- Controle de limites por plano

### 3. Banking (apps.banking)
**Funcionalidades:**
- Conexão via Pluggy (Open Banking)
- Sincronização de contas e transações
- Categorização (regras + automática via Pluggy)
- Orçamentos e metas

**Testes Prioritários:**
- Conexão de conta bancária
- Sincronização de transações
- Aplicação de regras de categorização
- Cálculos de orçamento

### 4. Categories (apps.categories)
**Funcionalidades:**
- Sistema hierárquico de categorias
- Regras de categorização automática
- Categorização manual/review

**Testes Prioritários:**
- CRUD de categorias
- Aplicação de regras
- Herança de categorias pai/filho

### 5. Reports (apps.reports)
**Funcionalidades:**
- Relatórios DRE, Fluxo de Caixa, Análise
- Exportação (PDF, Excel, CSV)
- Agendamento de relatórios
- Gráficos e visualizações

**Testes Prioritários:**
- Geração de relatórios
- Cálculos financeiros
- Exportação de formatos
- Agendamento

### 6. Notifications (apps.notifications)
**Funcionalidades:**
- Notificações in-app
- Email notifications
- WebSocket real-time
- Configurações por usuário

**Testes Prioritários:**
- Criação de notificações
- Envio por email
- WebSocket delivery
- Preferências usuário

### 7. Payments (apps.payments)
**Funcionalidades:**
- Stripe integration
- MercadoPago integration
- Webhook handling
- Subscription management

**Testes Prioritários:**
- Criação de customer
- Processamento de pagamento
- Webhook handling
- Subscription lifecycle

## Status de Desenvolvimento

### ✅ CONCLUÍDO
- **Fase 1.1**: Setup inicial backend Django ✅
- **Fase 1.2**: Modelo User customizado com TDD ✅ 
- **Fase 1.3**: Sistema autenticação JWT completo ✅
- **Fase 1.4**: Setup inicial frontend Next.js ✅
- **Fase 1.5**: Frontend autenticação (store, hooks, components) ✅
- **Fase 2.1**: Modelos Company e CompanyUser com TDD ✅
- **Fase 2.2**: Modelos Subscription e SubscriptionPlan com TDD ✅
- **Fase 2.3**: Permissões de empresa com TDD ✅
- **Fase 2.4**: Serializers de empresas com TDD ✅
- **Fase 2.5**: Views/API de empresas com TDD ✅
- **Fase 2.6**: Frontend Integration de empresas com TDD ✅
- **Fase 3.1**: Modelos Banking (BankProvider, BankAccount, Transaction) com TDD ✅
- **Fase 3.2**: Integração Pluggy (PluggyClient) com TDD ✅
- **Fase 3.3**: BankingService (sincronização completa) com TDD ✅
- **Fase 3.4**: Banking Serializers com TDD ✅
- **Fase 3.5**: Banking Views/API com TDD ✅  
- **Fase 3.6**: Banking URLs com TDD ✅
- **Fase 3.7**: Banking Tasks (sync_transactions) com TDD ✅
- **Fase 4.1**: Modelos Categories (Category, CategorizationRule) com TDD ✅
- **Fase 4.2**: Services de categorização (CategorizationService + RuleEngine) com TDD ✅
- **Fase 4.3**: Categories Serializers com TDD ✅
- **Fase 4.4**: Categories Views/API com TDD ✅
- **Fase 4.5**: Categories URLs com TDD ✅
- **Fase 4.6**: Categories Frontend Integration com TDD ✅
- **Fase 5.1**: Modelos Reports (Report, ScheduledReport) com TDD ✅

### 🚀 PRÓXIMAS FASES - ORDEM OBRIGATÓRIA

## 📍 PRÓXIMOS PASSOS IMEDIATOS

### 🎯 **BANKING TASKS CONCLUÍDAS!**

### ✅ Fase 3.7: Banking Tasks - CONCLUÍDA!
1. ✅ `test_sync_transactions.py` → `tasks.py` - Todas as 15 tasks implementadas
   - sync_account_transactions (com retry e rate limiting)
   - sync_all_company_accounts
   - sync_company_accounts_scheduled  
   - process_transaction_batch
   - categorize_transactions_batch

### ✅ Fase 4.6: Categories Frontend Integration - CONCLUÍDA! 
1. ✅ `test_categories_types.ts` → `types/categories.ts`
2. ✅ `test_categories_service.ts` → `services/categories.ts`
3. ✅ `test_categories_store.ts` → `store/categories.ts`
4. ✅ `test_useCategories.ts` → `hooks/useCategories.ts`
5. ✅ `test_CategorySelector.tsx` → `components/CategorySelector.tsx`

### ✅ Fase 3.8: Banking Frontend Integration - CONCLUÍDA!
1. ✅ `test_banking_types.ts` → `types/banking.ts`
2. ✅ `test_banking_service.ts` → `services/banking.ts` 
3. ✅ `test_banking_store.ts` → `store/banking.ts`
4. ✅ `test_useBanking.ts` → `hooks/useBanking.ts`
5. ✅ `test_AccountSelector.tsx` → `components/AccountSelector.tsx`

### ✅ Pendências Backend Menores - CONCLUÍDAS!
1. ✅ `test_rule_engine.py` → `services/rules.py` - CONCLUÍDO
   - **RuleEngine**: Motor flexível de regras com 8 operadores
   - **45 testes passando** (29 rule engine + 16 categorization service)
   - **91% cobertura** em ambos os serviços
   - **Operadores suportados**: EQUALS, CONTAINS, STARTS_WITH, ENDS_WITH, GREATER_THAN, LESS_THAN, REGEX, IN_LIST
   - **Features**: Cache de regras, múltiplas condições (AND/OR), performance otimizada

### ✅ Fase 5.1: Reports Models - CONCLUÍDA!
1. ✅ `test_report_model.py` → `models.py` (Report)
   - **10 testes passando** para modelo Report
   - **Features**: Status tracking, file management, metadata, processing time
   
2. ✅ `test_scheduled_report_model.py` → `models.py` (ScheduledReport)
   - **15 testes passando** para modelo ScheduledReport
   - **Features**: Multiple frequencies (daily/weekly/monthly/quarterly/yearly), recipient management, execution tracking
   - **Total: 25 testes passando com 94% cobertura nos models**

### Próximas Grandes Funcionalidades
1. ⏳ **Reports**: Services (ReportGenerator, PDFExporter), Views/API
2. ⏳ **Notifications**: Real-time, WebSocket  
3. ⏳ **Payments**: Stripe, MercadoPago, billing

## Fase 2: Multi-tenancy e Empresas (✅ CONCLUÍDO)
**📋 Ordem TDD concluída:**
1. **Backend Models**: ✅ CONCLUÍDO
   - ✅ `test_company_model.py` → `models.py` (Company, CompanyUser)
   - ✅ `test_subscription_model.py` → `models.py` (Subscription, SubscriptionPlan)
   - ✅ `test_company_permissions.py` → `permissions.py`

2. **Backend API**: ✅ CONCLUÍDO
   - ✅ `test_company_serializers.py` → `serializers.py`
   - ✅ `test_company_views.py` → `views.py` (CRUD empresas)
   - ✅ `test_company_urls.py` → `urls.py`

3. **Frontend Integration**: ✅ CONCLUÍDO
   - ✅ `test_company_types.ts` → `types/company.ts`
   - ✅ `test_company_service.ts` → `services/company.ts`
   - ✅ `test_company_store.ts` → `store/company.ts`
   - ✅ `test_useCompany.ts` → `hooks/useCompany.ts`
   - ✅ `test_CompanySelector.tsx` → `components/CompanySelector.tsx`

## Fase 3: Banking Integration (✅ CONCLUÍDO - Backend API)
**📋 Ordem TDD concluída:**
1. **Backend Models**: ✅ CONCLUÍDO
   - ✅ `test_bank_provider_model.py` → `models.py` (BankProvider)
   - ✅ `test_bank_account_model.py` → `models.py` (BankAccount)
   - ✅ `test_transaction_model.py` → `models.py` (Transaction)

2. **Pluggy Integration**: ✅ CONCLUÍDO
   - ✅ `test_pluggy_client.py` → `services/pluggy.py`
   - ✅ `test_banking_service.py` → `services/banking.py`
   - ✅ `test_sync_transactions.py` → `tasks.py` (CONCLUÍDO)

3. **Backend API**: ✅ CONCLUÍDO
   - ✅ `test_banking_serializers.py` → `serializers.py`
   - ✅ `test_banking_views.py` → `views.py`
   - ✅ `test_banking_urls.py` → `urls.py`
   - ✅ `test_banking_permissions.py` → `permissions.py`

4. **Frontend Integration**: ✅ CONCLUÍDO
   - ✅ Tipos, serviços, store, hooks e componentes para banking

## Fase 4: Categorização (✅ CONCLUÍDO - Backend + Frontend)
**📋 Ordem TDD concluída:**
1. **Backend Models**: ✅ CONCLUÍDO
   - ✅ `test_category_model.py` → `models.py`
   - ✅ `test_categorization_rule_model.py` → `models.py`

2. **Services**: ✅ CONCLUÍDO
   - ✅ `test_categorization_service.py` → `services/categorization.py`
   - ✅ `test_rule_engine.py` → `services/rules.py` (CONCLUÍDO)

3. **Backend API**: ✅ CONCLUÍDO
   - ✅ `test_categories_serializers.py` → `serializers.py`
   - ✅ `test_categories_views.py` → `views.py`
   - ✅ `test_categories_urls.py` → `urls.py`
   - ✅ `test_categories_permissions.py` → `permissions.py`

4. **Frontend Integration**: ✅ CONCLUÍDO
   - ✅ `test_categories_types.ts` → `types/categories.ts`
   - ✅ `test_categories_service.ts` → `services/categories.ts`
   - ✅ `test_categories_store.ts` → `store/categories.ts`
   - ✅ `test_useCategories.ts` → `hooks/useCategories.ts`
   - ✅ `test_CategorySelector.tsx` → `components/CategorySelector.tsx`

## Fase 5: Dashboard e Relatórios
**📋 Ordem TDD obrigatória:**
1. **Backend Models**:
   - `test_report_model.py` → `models.py`
   - `test_scheduled_report_model.py` → `models.py`

2. **Services**:
   - `test_report_generator.py` → `services/reports.py`
   - `test_dre_generator.py` → `services/generators/dre.py`
   - `test_cashflow_generator.py` → `services/generators/cashflow.py`

3. **Frontend**: Dashboard, gráficos, relatórios

## Fase 6: Notificações Real-time
**📋 Ordem TDD obrigatória:**
1. **Backend**:
   - `test_notification_model.py` → `models.py`
   - `test_notification_service.py` → `services/notifications.py`
   - `test_websocket_consumers.py` → `consumers.py`

2. **Frontend**: WebSocket, notificações real-time

## Fase 7: Pagamentos
**📋 Ordem TDD obrigatória:**
1. **Backend**:
   - `test_payment_model.py` → `models.py`
   - `test_stripe_service.py` → `services/stripe.py`
   - `test_mercadopago_service.py` → `services/mercadopago.py`
   - `test_webhook_handlers.py` → `views/webhooks.py`

2. **Frontend**: Checkout, gestão assinaturas

## Configurações Importantes

### Variáveis de Ambiente
```bash
# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/financedb
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
DEBUG=True

# Integrations
PLUGGY_CLIENT_ID=your-pluggy-client-id
PLUGGY_CLIENT_SECRET=your-pluggy-secret
STRIPE_SECRET_KEY=your-stripe-key
MERCADOPAGO_ACCESS_TOKEN=your-mercadopago-token

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Fixtures de Teste
```python
# Localização: backend/tests/fixtures/
@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def company_with_transactions(company):
    # Criar transações de exemplo
    return company
```

## Regras de Desenvolvimento

### Sempre Seguir TDD
1. **RED**: Escrever teste que falha primeiro
2. **GREEN**: Implementar código mínimo para passar
3. **REFACTOR**: Melhorar código mantendo testes verdes

### Cobertura de Testes
- **Meta**: >80% cobertura de código
- **Obrigatório**: Testar toda lógica de negócio
- **Prioridade**: Testes de integração para APIs

### Padrões de Código
- **Black** para formatação Python
- **isort** para imports Python
- **Prettier** para formatação TypeScript
- **ESLint** para linting TypeScript

### Commits
- Commits pequenos e focados
- Mensagens descritivas
- Sempre com testes passando

## Integrações Externas

### Pluggy (Open Banking)
```python
# Mock para testes
@patch('apps.banking.services.pluggy.PluggyClient')
def test_pluggy_integration(mock_pluggy):
    mock_pluggy.return_value.get_accounts.return_value = [...]
```

### Stripe (Pagamentos)
```python
# Mock para testes
@patch('stripe.Customer.create')
def test_create_customer(mock_create):
    mock_create.return_value = {'id': 'cus_123'}
```

## Comandos Úteis

### Teste Específico
```bash
# Backend
pytest apps/authentication/tests/test_models.py::TestUserModel::test_create_user

# Frontend
npm test -- --testNamePattern="should login user"
```

### Debug
```bash
# Backend
pytest --pdb  # Para debug no teste
python manage.py shell_plus  # Shell com imports

# Frontend
npm run dev  # Com hot reload
```

### Database
```bash
# Reset database
python manage.py flush
python manage.py migrate

# Backup
pg_dump financedb > backup.sql
```

## Notas Importantes

1. **Sempre teste primeiro** - Não implementar sem teste
2. **Um teste por vez** - Foque em fazer um passar
3. **Mocks para externos** - Pluggy, Stripe, emails, etc.
4. **Fixtures reutilizáveis** - Evite repetição
5. **Testes determinísticos** - Sempre mesmo resultado
6. **Cleanup após testes** - Dados limpos entre testes

Este arquivo será seu guia principal durante todo o desenvolvimento TDD do sistema.