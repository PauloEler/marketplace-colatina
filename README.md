# MERCADO COLATINA 🌿

Sistema local de compra e venda tipo OLX para a região de Colatina, ES.

---

## COMO RODAR

### 1. Instalar dependências (primeira vez)

```bash
pip install -r requirements.txt
```

### 2. Configurar ambiente local

Crie um arquivo `.env` local usando `.env.example` como modelo.

Nunca envie `.env`, banco real, uploads ou dados de usuários para o GitHub.

### 3. Iniciar o sistema

```bash
python app.py
```

### 4. Acessar no navegador

```text
http://localhost:5000
```

---

## CONFIGURAÇÃO DO ADMINISTRADOR

Este projeto pode criar um usuário administrador para testes locais.

Nunca use credenciais padrão em produção.

As credenciais de administrador devem ser configuradas localmente, fora do repositório, usando variáveis de ambiente ou procedimento seguro de criação de usuário.

Consulte:

- `.env.example`
- `docs/SEGURANCA.md`

Antes de colocar o sistema online, revise autenticação, criação do admin, senhas, uploads e chave secreta da aplicação.

---

## O QUE O SISTEMA FAZ

**Público (sem login):**

- Ver todos os anúncios
- Buscar por palavras e filtrar por categoria
- Ver detalhe de cada anúncio
- Contato direto pelo WhatsApp do vendedor

**Usuários cadastrados:**

- Criar anúncios com foto
- Ver e remover seus próprios anúncios

**Admin:**

- Cadastrar e desativar usuários
- Ativar/ocultar qualquer anúncio

---

## CATEGORIAS

Eletrônicos, Móveis, Roupas e Calçados, Veículos,
Eletrodomésticos, Imóveis, Serviços, Alimentos, Outros

---

## ESTRUTURA DOS ARQUIVOS

```text
marketplace/
├── app.py           — Servidor Flask (rotas)
├── database.py      — Banco de dados SQLite
├── requirements.txt
├── .env.example     — Modelo de variáveis locais
├── docs/            — Documentação técnica e segurança
├── uploads/         — Fotos dos anúncios (não versionar)
└── templates/
    ├── base.html
    ├── index.html
    ├── anuncio.html
    ├── login.html
    ├── criar.html
    ├── meus_anuncios.html
    └── admin.html
```

---

## SEGURANÇA

Este repositório deve guardar engenharia, não dados vivos.

Não envie para o GitHub:

- `.env` real;
- banco `marketplace.db` real;
- uploads reais;
- senhas reais;
- chaves Pix reais;
- dados reais de usuários.

---

## PRÓXIMOS PASSOS (quando quiser evoluir)

- [ ] Blindar criação do administrador
- [ ] Exigir `SECRET_KEY` segura em produção
- [ ] Revisar segurança de uploads
- [ ] Colocar online somente após auditoria
- [ ] IA dentro do sistema para gerar descrições de anúncios
- [ ] Sistema de avaliação de vendedores
- [ ] Anúncios em destaque (pagos)
- [ ] Notificação por WhatsApp quando alguém entrar em contato
