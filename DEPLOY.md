# Deploy

Para o TCC, a configuração recomendada é:

- frontend React na Vercel;
- API Django e PostgreSQL na Railway.

Essa separação evita manter um segundo processo web na Railway. O repositório inclui `backend/railway.json`, `render.yaml` e `frontend/vercel.json`; conectar o repositório a uma plataforma não cria serviços nas outras.

> A Railway oferece crédito gratuito limitado, não hospedagem ilimitada gratuita. Configure um limite de uso no painel e acompanhe `Usage` para não gerar cobranças. O PostgreSQL também consome recursos enquanto está ativo.

## 1. Backend e banco na Railway

1. Envie o repositório para o GitHub e crie um projeto na Railway a partir dele.
2. Crie um serviço PostgreSQL no mesmo projeto.
3. No serviço da API, configure:
   - **Root Directory:** `/backend`;
   - **Config File Path:** `/backend/railway.json`.
4. Gere um domínio público para a API em **Settings → Networking**.
5. Adicione as variáveis abaixo ao serviço da API:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=gere-uma-chave-longa-e-aleatoria
DEBUG=False
CORS_ALLOWED_ORIGINS=https://seu-frontend.vercel.app
CSRF_TRUSTED_ORIGINS=https://seu-frontend.vercel.app
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=0
LOG_LEVEL=INFO
```

`RAILWAY_PUBLIC_DOMAIN` é fornecida automaticamente pela plataforma e adicionada a `ALLOWED_HOSTS` pela aplicação. Se usar domínio próprio, inclua-o manualmente em `ALLOWED_HOSTS`.

O arquivo `railway.json` instala as dependências, coleta os arquivos estáticos, executa as migrations antes da publicação, inicia o Gunicorn e verifica `GET /api/health/`. Um único worker com duas threads reduz o consumo para este projeto pequeno.

Depois do primeiro deploy, abra um shell da API e crie o administrador:

```bash
python manage.py createsuperuser
```

Não execute `seed_demo` em produção com uma senha real. Se os dados fictícios forem necessários na apresentação, use uma senha descartável e remova os usuários depois.

## 2. Frontend na Vercel

1. Importe o mesmo repositório na Vercel.
2. Use `frontend` como **Root Directory**.
3. Configure a variável abaixo, usando o domínio público da API:

```env
VITE_API_URL=https://seu-backend.up.railway.app/api
```

4. Faça o deploy. `frontend/vercel.json` configura o build, a pasta `dist`, o fallback do React Router e os cabeçalhos básicos.
5. Copie a URL final da Vercel para `CORS_ALLOWED_ORIGINS` e `CSRF_TRUSTED_ORIGINS` na Railway e redeploye a API.

## 3. Controle de custo

- Ative o limite de uso/cobrança disponível no workspace da Railway antes do deploy.
- Consulte **Usage** depois de algumas horas e novamente antes da apresentação.
- Mantenha somente uma réplica e não adicione Redis, workers ou outros serviços para este TCC.
- Se a conta permitir Serverless/App Sleeping, habilite-o para a API; a primeira requisição após inatividade poderá ser mais lenta.
- Desative ou remova os serviços depois da banca caso não precise mais deles. Exporte antes qualquer dado que queira preservar.

## 4. Validação

Antes de apresentar, confirme:

- `https://seu-backend.up.railway.app/api/health/` retorna `{"status":"ok","database":"ok"}`;
- login, refresh do token e permissões dos três perfis funcionam;
- uma reserva pode ser solicitada, aprovada e consultada;
- `DEBUG=False` e nenhum segredo foi versionado;
- o banco possui backup ou ao menos um `pg_dump` recente, se os dados forem importantes.

Comece com `SECURE_HSTS_SECONDS=0`. Somente altere para `31536000` depois de confirmar que todos os domínios funcionam exclusivamente por HTTPS.

## Alternativa Render

O `render.yaml` foi preservado como alternativa. Não conecte simultaneamente Render e Railway ao mesmo banco sem uma necessidade clara, pois isso duplica serviços e pode aumentar consumo ou causar deploys concorrentes.
