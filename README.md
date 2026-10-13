# Sistema de Reserva de Laboratórios

## Sobre

Aplicação full stack para consulta, solicitação, aprovação e acompanhamento de reservas de laboratórios acadêmicos. React consome exclusivamente a API REST Django; PostgreSQL é o banco do produto final.

## Objetivos e funcionalidades

- Catálogo e ativação/desativação de laboratórios.
- Disponibilidade por laboratório, data e intervalo opcional.
- Solicitações pendentes por professores.
- Aprovação, rejeição e cancelamento lógico, com histórico preservado.
- Prevenção transacional de sobreposição entre reservas aprovadas.
- JWT, interfaces e autorização backend por grupos.
- Filtros administrativos e gestão de perfis de usuários.

## Perfis

- **Aluno:** consulta laboratórios e disponibilidade.
- **Professor:** também solicita, acompanha e cancela suas reservas.
- **Administrador:** gerencia laboratórios, solicitações, histórico e perfis. O grupo Administradores é distinto de `is_superuser`.

## Tecnologias e arquitetura

React 19, Vite, React Router e Axios → HTTP/JSON → Django 6, Django REST Framework e SimpleJWT → Django ORM → PostgreSQL. SQLite é apenas fallback local, preservado para desenvolvimento.

```text
backend/
  config/          configurações e rotas
  laboratorios/    modelo, API, admin e testes
  reservas/        regras, API, seed, admin e testes
  usuarios/        usuário atual e gestão de perfis
frontend/
  src/services/    cliente Axios e refresh JWT
  src/routes/      proteção por autenticação/perfil
  src/App.jsx      interface responsiva por perfil
DEPLOY.md
```

## Requisitos

Python 3.12+, Node.js 20+ e PostgreSQL 15+ para o ambiente final.

## Variáveis de ambiente

Copie `backend/.env.example` para `backend/.env` e `frontend/.env.example` para `frontend/.env`. Configure `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` e `VITE_API_URL`. Arquivos `.env` são ignorados pelo Git.

## Backend e PostgreSQL

Crie previamente o banco e o usuário no PostgreSQL, conceda acesso e informe as credenciais no `.env`:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo --password "uma-senha-apenas-local"
python manage.py runserver
```

As migrations existentes são preservadas. Para validar mudanças: `python manage.py makemigrations --check`.

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`; a API local padrão é `http://127.0.0.1:8000/api`.

## Dados de demonstração

`seed_demo` é idempotente e cria os grupos, três laboratórios e `aluno.demo`, `professor.demo` e `admin.demo`. A senha é obrigatoriamente escolhida pelo operador via `--password`; use apenas credenciais descartáveis locais.

## API

| Método | URL | Perfil | Descrição |
|---|---|---|---|
| POST | `/api/auth/login/` | Público | Obtém access/refresh JWT |
| POST | `/api/auth/register/` | Público | Cria uma conta exclusivamente com perfil Aluno |
| POST | `/api/auth/refresh/` | Token refresh | Renova access token |
| GET | `/api/auth/me/` | Autenticado | Usuário e perfil atual |
| GET | `/api/laboratorios/` | Autenticado | Lista laboratórios |
| POST/PATCH | `/api/laboratorios/`, `/api/laboratorios/{id}/` | Administrador | Cadastra/edita/ativa |
| GET | `/api/laboratorios/{id}/disponibilidade/?data=AAAA-MM-DD` | Autenticado | Ocupações aprovadas |
| GET | `/api/agenda/?data_inicio=AAAA-MM-DD&data_fim=AAAA-MM-DD` | Autenticado | Calendário de ocupações aprovadas |
| GET | `/api/reservas/` | Professor/Admin | Histórico visível e filtros |
| POST | `/api/reservas/` | Professor | Cria solicitação pendente |
| POST | `/api/reservas/{id}/aprovar/` | Administrador | Aprova ou retorna 409 em conflito |
| POST | `/api/reservas/{id}/rejeitar/` | Administrador | Rejeita sem excluir |
| POST | `/api/reservas/{id}/cancelar/` | Dono/Admin | Cancela sem excluir |
| GET/PATCH | `/api/usuarios/`, `/api/usuarios/{id}/` | Administrador | Consulta e atribui perfil |

Filtros de reservas: `status`, `laboratorio`, `professor` (admin), `data`, `data_inicio` e `data_fim`.

## Testes

```powershell
cd backend
python manage.py check
python manage.py makemigrations --check
python manage.py test
cd ../frontend
npm run build
```

## Deploy

Consulte [DEPLOY.md](DEPLOY.md). O projeto inclui `render.yaml`, health check, Gunicorn, WhiteNoise, suporte a `DATABASE_URL` e `frontend/vercel.json`. Não há deploy automático nem URLs/credenciais de produção no código.
