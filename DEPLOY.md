# Deploy

O repositório inclui `render.yaml` para backend/banco e `frontend/vercel.json` para o frontend. Nenhum serviço é criado automaticamente até o blueprint/projeto ser conectado nos respectivos painéis.

## Arquitetura sugerida

- Frontend React em Vercel ou serviço estático equivalente.
- Django/DRF em serviço Python com HTTPS e processo WSGI (`config.wsgi`).
- PostgreSQL gerenciado com backups e TLS.

## Backend

Defina `SECRET_KEY` forte, `DEBUG=False`, hosts/origens exatos e todas as variáveis `DB_*`. Instale `backend/requirements.txt`, execute `python manage.py migrate`, `python manage.py collectstatic --noinput` e inicie o servidor WSGI oferecido pela plataforma. Crie superusuário por console seguro, nunca em fixture.

### Render

1. Envie o repositório para o GitHub.
2. No Render, crie um Blueprint a partir de `render.yaml`.
3. Preencha as variáveis marcadas com `sync: false`:
   - `ALLOWED_HOSTS`: hostname do backend, sem `https://`;
   - `CORS_ALLOWED_ORIGINS`: URL HTTPS completa da Vercel;
   - `CSRF_TRUSTED_ORIGINS`: a mesma URL HTTPS do frontend.
4. O blueprint gera `SECRET_KEY`, conecta `DATABASE_URL`, executa migrations, coleta estáticos e inicia Gunicorn.
5. Após o primeiro deploy, crie o superusuário no Shell: `python backend/manage.py createsuperuser`.

O endpoint público `GET /api/health/` valida a aplicação e a conexão com o banco e é usado pelo health check do Render.

Antes de liberar, rode `python manage.py check --deploy` e os testes. Restrinja o banco à rede do backend, habilite backups e mantenha logs sem tokens ou senhas.

## Frontend

Configure `VITE_API_URL=https://api.seu-dominio/api`, execute `npm ci` e `npm run build`, e publique `frontend/dist`. Configure fallback de SPA para `index.html` e HTTPS.

### Vercel

1. Importe o mesmo repositório e use `frontend` como Root Directory.
2. Configure `VITE_API_URL` com a URL final do backend acrescida de `/api`.
3. Faça o deploy. `frontend/vercel.json` configura build, saída `dist`, fallback do React Router, cache dos assets e cabeçalhos básicos.
4. Volte ao Render e preencha CORS/CSRF com a URL criada pela Vercel; então faça novo deploy do backend.

## CORS e segurança

`CORS_ALLOWED_ORIGINS` deve conter somente a URL HTTPS real do frontend. Configure cabeçalhos seguros e proxy HTTPS na plataforma. Tokens permanecem no armazenamento do navegador nesta implementação; para um ambiente de maior risco, a evolução recomendada é refresh token em cookie HttpOnly/Secure com proteção CSRF.

Comece com `SECURE_HSTS_SECONDS=0`. Depois de confirmar que todos os domínios funcionam exclusivamente por HTTPS, altere para `31536000`. Não ative HSTS antecipadamente em domínio que ainda precise responder por HTTP.

## Checklist

- Migrations e testes passaram no banco PostgreSQL de homologação.
- `DEBUG=False`, segredo e credenciais estão no cofre da plataforma.
- Hosts, CORS e URL da API usam os domínios finais.
- Arquivos estáticos, HTTPS, logs, backups e monitoramento estão ativos.
- Fluxo Aluno → Professor → Administrador foi validado em homologação.
