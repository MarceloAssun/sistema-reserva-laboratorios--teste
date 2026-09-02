# ReservaLab

Protótipo de uma plataforma web para consulta e reserva de laboratórios acadêmicos. O frontend React conversa com uma API REST Django REST Framework; o banco recomendado para execução é PostgreSQL.

## Tecnologias

- Python 3.12+
- Django 6
- Django REST Framework e JWT
- PostgreSQL (SQLite é usado apenas como fallback local quando `DB_NAME` não está configurado)
- React 19, Vite e Axios

## Configuração do backend

No PowerShell, a partir de `backend/`:

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_demo --password demo1234
python manage.py runserver
```

O comando `seed_demo` cria os grupos `Alunos`, `Professores` e `Administradores`, três usuários de demonstração e laboratórios de exemplo. A senha acima é somente para demonstração local:

- `aluno.demo`
- `professor.demo`
- `admin.demo`

Para PostgreSQL, preencha `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` e `DB_PORT` no `.env` antes de executar as migrations. Nunca versione o `.env`.

## Configuração do frontend

Em outro terminal, a partir de `frontend/`:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Abra `http://localhost:5173`. O backend fica em `http://localhost:8000`.

## API principal

- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/`
- `GET /api/laboratorios/`
- `POST/PATCH /api/laboratorios/` (administrador)
- `GET/POST /api/reservas/`
- `POST /api/reservas/{id}/aprovar/` (administrador)
- `POST /api/reservas/{id}/rejeitar/` (administrador)
- `POST /api/reservas/{id}/cancelar/` (dono ou administrador)
- `GET /api/disponibilidade/?laboratorio=1&data=2026-09-10`

A API limita reservas por perfil, mantém cancelamentos no banco e verifica novamente conflitos no momento da aprovação. Duas reservas aprovadas no mesmo laboratório só entram em conflito quando os intervalos se sobrepõem.

## Testes

```powershell
Set-Location backend
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py test
```

## Estrutura

```text
backend/
  config/                 Configuração e URLs
  laboratorios/           Modelo e API de laboratórios
  reservas/               Modelo, regras, permissões e API de reservas
frontend/
  src/App.jsx             Interface demonstrável por perfil
  src/services/api.js     Cliente HTTP centralizado
```
