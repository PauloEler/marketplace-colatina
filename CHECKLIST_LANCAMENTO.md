# Checklist de lançamento — Mercado Colatina

Atualizado em 12 de julho de 2026.

## Concluído e verificado no projeto

- Cadastro, login, alteração de senha, atualização e desativação da conta.
- Aceite dos Termos de Uso e da Política de Privacidade registrado no banco.
- Proteção CSRF e bloqueio temporário de tentativas repetidas de login.
- Anúncios com bairro, busca, até cinco fotos, edição, pausa e reativação.
- Pedidos com confirmação, recusa, cancelamento, conclusão e regras de reativação.
- Contato por WhatsApp com medição de conversão.
- Denúncias, moderação e indicadores administrativos.
- Plano gratuito, assinatura por PIX e integração opcional com Mercado Pago.
- Neo opcional para rascunhos de anúncios, com revisão humana obrigatória.
- Layout revisado em computador e celular.
- Testes automáticos executados durante a publicação.
- Inicialização e esquema validados com PostgreSQL 16.
- Produção impedida de iniciar sem banco permanente, Cloudinary e dados administrativos.

## Obrigatório antes de abrir ao público

- [ ] Confirmar no Render os valores reais de `ADMIN_WHATSAPP`, `SUPPORT_WHATSAPP`, `PIX_KEY` e `PIX_RECEIVER_NAME`.
- [ ] Informar `CLOUDINARY_URL` e confirmar o envio de fotos no ambiente publicado.
- [ ] Confirmar que o PostgreSQL do Render está com backup automático habilitado e testar uma restauração.
- [ ] Revisar Termos de Uso e Política de Privacidade com o responsável legal pelo negócio.
- [ ] Conectar o domínio oficial e verificar HTTPS, `robots.txt` e `sitemap.xml`.
- [ ] Criar duas contas reais de teste e executar uma compra completa em produção.
- [ ] Definir se o primeiro lançamento usará somente negociação por WhatsApp ou também Mercado Pago.
- [ ] Se Mercado Pago for ativado, preencher `MP_CLIENT_SECRET` e `MP_WEBHOOK_SECRET` e validar pagamento, recusa e estorno em ambiente controlado.
- [ ] Se o Neo for ativado, preencher `OPENAI_API_KEY`, definir um limite mensal de gastos e testar anúncios permitidos e proibidos.
- [ ] Configurar alertas do Render para indisponibilidade e erros da aplicação.

## Comando de verificação

```powershell
python -m unittest discover -s tests -v
```

O lançamento só deve ser anunciado depois que todos os itens obrigatórios acima estiverem confirmados no ambiente publicado.
