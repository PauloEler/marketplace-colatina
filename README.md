# Mercado Colatina

Marketplace local em Flask para compra e venda na regiao de Colatina.

## Pronto para publicacao

O projeto agora inclui:

- senhas com hash
- validacao de formularios
- protecao CSRF nos `POST`
- cookies de sessao endurecidos para producao
- rota de health check em `/health`
- `Procfile` com `gunicorn`
- variaveis de ambiente documentadas

## Requisitos

- Python 3.11
- `pip`

## Instalar

```bash
pip install -r requirements.txt
```

## Variaveis de ambiente

Copie `.env.example` e configure:

- `SECRET_KEY`: obrigatoria em producao
- `FLASK_ENV`: use `production` em deploy
- `PORT`: porta do servidor
- `DATABASE_PATH`: caminho do arquivo SQLite
- `UPLOAD_FOLDER`: pasta onde as imagens enviadas serao salvas

## Rodar localmente

```bash
python app.py
```

Abra:

- pagina inicial: `http://localhost:5000`
- admin: `http://localhost:5000/admin`

## Deploy

### Render / Railway / Heroku-like

Use:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

Defina pelo menos:

- `SECRET_KEY`
- `FLASK_ENV=production`
- `DATABASE_PATH`
- `UPLOAD_FOLDER`
- `ADMIN_PASSWORD`

### Render com Blueprint

Este repositorio ja inclui `render.yaml`, entao voce pode criar a infra direto pelo Render Blueprint.

Link de deploy:

`https://render.com/deploy?repo=https://github.com/PauloEler/marketplace-colatina`

## Persistencia

Se publicar em uma plataforma com filesystem temporario, configure volume/disco persistente para:

- banco SQLite
- pasta de uploads

Sem isso, imagens e banco podem ser perdidos a cada novo deploy.

No Render Free, o Postgres fica persistente, mas a pasta de uploads continua efemera. Isso significa que fotos enviadas podem sumir em restart ou redeploy. Para uso real em producao, o ideal e:

- usar um plano pago com persistent disk
- ou mover uploads para armazenamento externo

## Observacoes

- O usuario `admin` e criado automaticamente se ainda nao existir.
- Em producao, o admin inicial depende de `ADMIN_USERNAME` e `ADMIN_PASSWORD`.
- O banco SQLite e inicializado na subida da aplicacao.
- Arquivos acima de 5 MB sao rejeitados.
