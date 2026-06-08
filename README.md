# MERCADO COLATINA 🌿

Sistema local de compra e venda tipo OLX para a região de Colatina, ES.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

Acesse:

```text
http://localhost:5000
```

## Configuração segura

Crie um arquivo `.env` local usando `.env.example` como modelo.

Nunca envie para o GitHub:

- `.env` real;
- banco real;
- uploads reais;
- senhas reais;
- chaves Pix reais;
- dados reais de usuários.

## Administrador

O administrador inicial deve ser configurado por variáveis de ambiente:

```env
ADMIN_USERNAME=admin_local
ADMIN_PASSWORD=troque-esta-senha
ADMIN_NOME=Administrador
ADMIN_WHATSAPP=
```

Nunca use credenciais padrão em produção.

Consulte `docs/SEGURANCA.md` antes de colocar online.

## O que o sistema faz

**Público:**

- Ver anúncios.
- Buscar por palavra e categoria.
- Ver detalhes do anúncio.
- Contato pelo WhatsApp do vendedor.

**Usuários:**

- Criar anúncios com foto.
- Ver e remover próprios anúncios.

**Admin:**

- Cadastrar e desativar usuários.
- Ativar ou ocultar anúncios.

## Estrutura básica

```text
marketplace/
├── app.py
├── database.py
├── requirements.txt
├── .env.example
├── docs/
├── uploads/      # não versionar
└── templates/
```

## Próximos passos

- [ ] Testar a consolidação de segurança.
- [ ] Revisar produção antes de publicar online.
- [ ] Validar imagens com verificação profunda.
- [ ] Implementar limite de tentativas de login.
- [ ] Criar política mínima de senha.
