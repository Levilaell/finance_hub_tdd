# CLAUDE.md

Este arquivo fornece contexto completo ao Claude Code para desenvolvimento TDD do Sistema de Gestão Financeira.

## Projeto Overview

**Sistema SaaS de Gestão Financeira** para PMEs brasileiras com integração bancária via Open Banking, categorização automática, relatórios avançados e gestão multi-empresa.

**Metodologia**: Test-Driven Development (TDD) - RED → GREEN → REFACTOR

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

## Plano de Desenvolvimento por Fases

### Fase 1: Setup e Autenticação
**Ordem TDD:**
1. Testes modelo User → Implementar modelo
2. Testes JWT auth → Implementar views
3. Testes 2FA → Implementar funcionalidade
4. Testes frontend auth → Implementar páginas

### Fase 2: Multi-tenancy
**Ordem TDD:**
1. Testes modelo Company → Implementar modelo
2. Testes Subscription → Implementar assinaturas
3. Testes permissions → Implementar controle acesso
4. Testes frontend company → Implementar UI

### Fase 3: Banking Integration
**Ordem TDD:**
1. Testes modelo BankAccount → Implementar modelo
2. Testes Pluggy integration → Implementar serviço
3. Testes sync transactions → Implementar sincronização
4. Testes categorization → Implementar regras
5. Testes frontend banking → Implementar UI

### Fase 4: Relatórios
**Ordem TDD:**
1. Testes geração relatórios → Implementar generators
2. Testes exportação → Implementar exporters
3. Testes agendamento → Implementar scheduler
4. Testes frontend reports → Implementar UI

### Fase 5: Real-time Features
**Ordem TDD:**
1. Testes notifications → Implementar sistema
2. Testes WebSocket → Implementar consumers
3. Testes email → Implementar templates
4. Testes frontend real-time → Implementar UI

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