# Mercado Colatina

Marketplace local em Flask para compra e venda em Colatina e região.

## Estrutura de produção

- Flask e Gunicorn para a aplicação.
- PostgreSQL para contas, anúncios e planos.
- Cloudinary para armazenamento permanente e otimização das fotos.
- Render para hospedagem, HTTPS, banco e domínio personalizado.
- PIX direto para o responsável, com solicitação registrada e aprovação pelo painel administrativo.

## Executar localmente

1. Crie um ambiente virtual.
2. Instale as dependências com `pip install -r requirements.txt`.
3. Copie `.env.example` para `.env` e preencha os valores locais.
4. Defina `FLASK_ENV=development`.
5. Execute `python app.py`.

Sem `DATABASE_URL`, o projeto usa SQLite. Sem `CLOUDINARY_URL`, as imagens são salvas na pasta local de uploads.

## Publicar no Render

O arquivo `render.yaml` cria um serviço web e um PostgreSQL permanente na região da Virgínia. Durante a criação:

1. Conecte o repositório ao Render.
2. Crie o Blueprint usando `render.yaml`.
3. Informe a variável secreta `CLOUDINARY_URL`.
4. Aguarde o health check em `/health` ficar disponível.
5. Depois dos testes, conecte o domínio personalizado.

Nunca salve senhas, chaves do banco ou a credencial do Cloudinary no repositório.

## Antes do lançamento

- Revisar Termos de Uso e Privacidade.
- Trocar a chave PIX e os dados administrativos pelos dados oficiais.
- Testar cadastro, login, edição, pausa e reativação de anúncios.
- Configurar backups e monitoramento.
- Integrar o pagamento automático quando as credenciais do Mercado Pago estiverem disponíveis.
