# RELATÓRIO — DEVOPS SPRINT 001

## 1. Resumo executivo

A DevOps Sprint 001 separa definitivamente validação e publicação no Mercado Colatina. Pull Requests passam a executar exclusivamente CI, branches de desenvolvimento deixam de ter qualquer vínculo com produção e o Render passa a aceitar publicação automática apenas a partir da `master`, depois da aprovação dos checks dessa branch.

Nenhum arquivo da aplicação, banco de dados, modelo, migration ou regra de negócio foi alterado.

## 2. Diagnóstico da configuração anterior

### GitHub Actions

O workflow `.github/workflows/ci.yml` estava limitado à branch técnica `agent/profissionalizar-marketplace`:

- Pull Requests só disparavam CI quando apontavam para essa branch;
- pushes nessa mesma branch disparavam CI;
- Pull Requests direcionadas à `master` não possuíam validação automática;
- a branch técnica era usada simultaneamente como superfície de CI e origem de produção.

### GitHub

O repositório ainda tinha `main` como branch padrão, embora a linha de integração e produção adotada pelo projeto fosse `master`. Isso aumentava o risco de novas Pull Requests utilizarem a base incorreta.

### Render

O serviço `mercado-colatina` monitorava `agent/profissionalizar-marketplace` com deploy automático a cada commit. Como consequência, um push utilizado apenas para executar CI também podia publicar código em produção antes do merge formal.

Configuração observada antes da Sprint:

- branch do Render: `agent/profissionalizar-marketplace`;
- auto-deploy: `On Commit`;
- health check: `/health`;
- build: `pip install -r requirements.txt`;
- start: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60`.

## 3. Nova arquitetura do pipeline

```text
Branch de desenvolvimento
        ↓
Pull Request para master
        ↓
GitHub Actions: Ruff + formatação + testes
        ↓
Revisão e merge
        ↓
Push resultante na master
        ↓
GitHub Actions valida a master
        ↓
Render aguarda checks aprovados
        ↓
Deploy automático da master
        ↓
Health check /health
```

### GitHub Actions

O workflow passa a responder somente a:

- `pull_request` com destino à `master`;
- `push` na `master`, normalmente produzido pelo merge de uma Pull Request.

O workflow não possui qualquer etapa, credencial ou chamada de deploy. Sua responsabilidade é exclusivamente:

1. baixar o código;
2. preparar Python 3.13;
3. instalar dependências e Ruff;
4. executar `ruff check .`;
5. executar `ruff format --check .`;
6. executar todos os testes automatizados.

Também foram aplicados:

- concorrência por workflow e referência, cancelando validações obsoletas;
- timeout de 15 minutos;
- permissões mínimas de leitura;
- `actions/checkout@v5` e `actions/setup-python@v6`, baseados em Node.js 24.

### Render

O serviço e o Blueprint passam a declarar explicitamente:

- branch: `master`;
- `autoDeployTrigger: checksPass`;
- health check: `/health`.

Assim, commits de branches de desenvolvimento são ignorados pelo Render. Mesmo na `master`, a publicação aguarda a aprovação dos checks associados ao commit.

### Branch padrão

A branch padrão do GitHub passa de `main` para `master`, alinhando criação de Pull Requests, integração, CI e deploy.

## 4. Divisão de responsabilidades

| Responsabilidade | Configuração |
|---|---|
| Desenvolvimento | branches `agent/*`, `feature/*`, `hotfix/*` e equivalentes |
| CI de Pull Request | GitHub Actions em PR com base `master` |
| CI pós-merge | GitHub Actions em push na `master` |
| Deploy | Render, exclusivamente a partir da `master` |
| Gatilho do deploy | checks da `master` aprovados |
| Disponibilidade | health check HTTP em `/health` |

## 5. Arquivos de infraestrutura alterados

- `.github/workflows/ci.yml`;
- `render.yaml`;
- `RELATORIO_DEVOPS_SPRINT_001.md`.

Nenhum HTML, CSS, JavaScript, arquivo Python da aplicação, banco, migration ou regra de negócio faz parte da Sprint.

## 6. Validações planejadas e executadas

### Validação local

- `git diff --check`: aprovado;
- sintaxe YAML de `.github/workflows/ci.yml` e `render.yaml`: aprovada;
- `ruff check .`: aprovado;
- `ruff format --check .`: 8 arquivos já formatados;
- suíte automatizada: 81/81 testes aprovados em 10,246 segundos;
- confirmação de que o relatório de auditoria UX permaneceu fora do commit.

### Validação remota

- CI da mudança de DevOps;
- ausência de deployment após push em branch não produtiva;
- CI em Pull Request para `master`;
- CI pós-merge na `master`;
- deploy automático do mesmo hash da `master` após checks aprovados;
- build e inicialização no Render;
- health check HTTP 200;
- Home de produção acessível;
- ausência de `ERROR`, `Traceback`, `Exception` e HTTP 500 nos sinais verificados.

Os hashes, URLs e resultados finais são registrados na entrega da Sprint após a conclusão das validações remotas.

### Correção inicial do ambiente de produção

Antes da integração desta Sprint, o painel do Render foi corrigido para observar `master`. A alteração iniciou automaticamente um deploy corretivo do hash então vigente na `master`, `7edfd223bcf1bf9da0564096bc0ae956cf518b68`, com os seguintes resultados:

- build concluído com sucesso;
- Gunicorn iniciado com dois workers;
- serviço marcado como `live`;
- verificações internas de `/health` retornando HTTP 200;
- Health Check externo retornando HTTP 200 e `{"status":"ok"}`;
- Home retornando HTTP 200;
- nenhum `ERROR`, `Traceback`, `Exception` ou HTTP 500 identificado nos logs observados.

Em seguida, o auto-deploy do serviço foi alterado de `On Commit` para `After CI Checks Pass`, preparando o fluxo definitivo que será consolidado pelo `render.yaml` desta Sprint.

## 7. Riscos eliminados

- deploy acidental ao usar uma branch técnica para CI;
- publicação de código de Pull Request antes do merge;
- divergência entre branch padrão, branch de integração e branch de produção;
- Pull Requests para `master` sem testes automáticos;
- deploy da `master` antes da conclusão dos checks;
- execuções concorrentes e obsoletas do mesmo workflow;
- uso de actions baseadas no runtime Node.js 20 depreciado;
- configuração de branch do Render dependente apenas do painel externo.

## 8. Regras permanentes

1. Toda mudança deve partir de uma branch de desenvolvimento.
2. Toda integração deve ocorrer por Pull Request para `master`.
3. Pull Requests executam apenas CI.
4. GitHub Actions não executa deploy.
5. Apenas a `master` pode ser monitorada pelo Render.
6. O Render publica somente depois que os checks da `master` forem aprovados.
7. Banco de dados e regras de negócio permanecem fora do pipeline de validação e deploy.

## 9. Resultado esperado

O pipeline passa a representar um fluxo profissional e auditável:

**desenvolvimento → Pull Request → CI → revisão → merge na master → CI da master → deploy no Render → health check.**
