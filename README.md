# MERCADO COLATINA 🌿
Sistema local de compra e venda tipo OLX para a região de Colatina, ES.

---

## COMO RODAR

### 1. Instalar dependências (primeira vez)
```
pip install flask
```

### 2. Iniciar o sistema
```
python app.py
```

### 3. Acessar no navegador
```
http://localhost:5000
```

---

## LOGIN ADMIN (padrão)
- Usuário: `admin`
- Senha: `admin123`
- Painel admin: `http://localhost:5000/admin`

⚠️ Mude a senha do admin pelo banco de dados após o primeiro acesso.

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

**Admin (você):**
- Cadastrar e desativar usuários
- Ativar/ocultar qualquer anúncio

---

## CATEGORIAS
Eletrônicos, Móveis, Roupas e Calçados, Veículos,
Eletrodomésticos, Imóveis, Serviços, Alimentos, Outros

---

## ESTRUTURA DOS ARQUIVOS
```
marketplace/
├── app.py           — Servidor Flask (rotas)
├── database.py      — Banco de dados SQLite
├── marketplace.db   — Banco (criado automaticamente)
├── requirements.txt
├── uploads/         — Fotos dos anúncios
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

## PRÓXIMOS PASSOS (quando quiser evoluir)
- [ ] Colocar online (Heroku, Railway, VPS)
- [ ] IA dentro do sistema para gerar descrições de anúncios
- [ ] Sistema de avaliação de vendedores
- [ ] Anúncios em destaque (pagos)
- [ ] Notificação por WhatsApp quando alguém entrar em contato
