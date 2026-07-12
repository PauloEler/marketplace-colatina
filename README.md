# Mercado Colatina

Marketplace local em Flask para compra e venda em Colatina e região.

## Estrutura de produção

- Flask e Gunicorn para a aplicação.
- PostgreSQL para contas, anúncios e planos.
- Cloudinary para armazenamento permanente e otimização das fotos.
- Render para hospedagem, HTTPS, banco e domínio personalizado.
- PIX direto para o responsável, com solicitação registrada e aprovação pelo painel administrativo.
- Denúncias de anúncios com fila de moderação e decisão humana no painel administrativo.
- Aceite registrado dos Termos de Uso e da Política de Privacidade.
- Edição de dados pessoais, recuperação de acesso, ajuda e desativação segura da conta.
- Anúncios com bairro, busca por localização e galeria de até cinco fotos.
- Indicadores administrativos de usuários, anúncios, contatos, pedidos e moderação.
- Neo opcional para criar rascunhos de anúncios com IA e revisão obrigatória do vendedor.

## Executar localmente

1. Crie um ambiente virtual.
2. Instale as dependências com `pip install -r requirements.txt`.
3. Copie `.env.example` para `.env` e preencha os valores locais.
4. Defina `FLASK_ENV=development`.
5. Execute `python app.py`.

Sem `DATABASE_URL`, o projeto usa SQLite. Sem `CLOUDINARY_URL`, as imagens são salvas na pasta local de uploads.

## Testes automáticos

Execute `python -m unittest discover -s tests -v` para validar o fluxo de denúncias e moderação sem alterar o banco de desenvolvimento.

## Publicar no Render

O arquivo `render.yaml` cria um serviço web e um PostgreSQL permanente na região da Virgínia. Durante a criação:

1. Conecte o repositório ao Render.
2. Crie o Blueprint usando `render.yaml`.
3. Informe a variável secreta `CLOUDINARY_URL`.
4. Para ativar o Neo, informe também `OPENAI_API_KEY`. Sem essa chave, o restante do marketplace funciona normalmente.
5. Aguarde o health check em `/health` ficar disponível.
6. Depois dos testes, conecte o domínio personalizado.

O processo de publicação executa os testes automaticamente e interrompe a atualização se algum fluxo essencial falhar.

Use também o [checklist de lançamento](CHECKLIST_LANCAMENTO.md) para configurar e validar o ambiente real antes de abrir o marketplace ao público.

Nunca salve senhas, chaves do banco ou a credencial do Cloudinary no repositório.

Em `FLASK_ENV=production`, a aplicação não inicia sem `DATABASE_URL`, `CLOUDINARY_URL`, `ADMIN_PASSWORD`, `ADMIN_WHATSAPP`, `PIX_KEY` e `SUPPORT_WHATSAPP`. Essa validação evita publicar o site com banco ou fotos temporárias.

## Antes do lançamento

- Revisar Termos de Uso e Privacidade.
- Trocar a chave PIX e os dados administrativos pelos dados oficiais.
- Testar cadastro, login, edição, pausa e reativação de anúncios.
- Configurar backups e monitoramento.
- Integrar o pagamento automático quando as credenciais do Mercado Pago estiverem disponíveis.
