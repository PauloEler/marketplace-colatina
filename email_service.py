import os
import smtplib
from email.message import EmailMessage


def destinatario_admin():
    return os.environ.get("ADMIN_NOTIFICATION_EMAIL", "").strip()


def email_configurado():
    obrigatorios = (
        "SMTP_HOST",
        "SMTP_USERNAME",
        "SMTP_PASSWORD",
        "SMTP_FROM_EMAIL",
    )
    return bool(destinatario_admin()) and all(
        os.environ.get(nome, "").strip() for nome in obrigatorios
    )


def enviar_alerta_novo_pedido(pedido, painel_url):
    """Envia o aviso sem expor credenciais e sem interromper a compra."""
    if not email_configurado():
        return "aguardando_configuracao"

    mensagem = EmailMessage()
    mensagem["Subject"] = (
        f"[ALERTA DE VENDA] Novo pedido #{pedido['id']} - {pedido['titulo']}"
    )
    mensagem["From"] = os.environ["SMTP_FROM_EMAIL"].strip()
    mensagem["To"] = destinatario_admin()
    mensagem.set_content(
        "NOVO PEDIDO NO MERCADO COLATINA\n\n"
        f"Pedido: #{pedido['id']}\n"
        f"Produto: {pedido['titulo']}\n"
        f"Valor: R$ {pedido['valor']}\n"
        f"Comprador: {pedido['comprador_nome']}\n"
        f"Vendedor: {pedido['vendedor_nome']}\n"
        f"Entrega: {pedido['entrega']}\n"
        f"Observacao: {pedido['observacao'] or '-'}\n\n"
        f"Abra o painel administrativo: {painel_url}\n"
    )

    host = os.environ["SMTP_HOST"].strip()
    porta = int(os.environ.get("SMTP_PORT", "587"))
    usuario = os.environ["SMTP_USERNAME"].strip()
    senha = os.environ["SMTP_PASSWORD"]
    usar_ssl = os.environ.get("SMTP_USE_SSL", "false").lower() == "true"

    cliente_cls = smtplib.SMTP_SSL if usar_ssl else smtplib.SMTP
    with cliente_cls(host, porta, timeout=8) as cliente:
        if not usar_ssl:
            cliente.starttls()
        cliente.login(usuario, senha)
        cliente.send_message(mensagem)
    return "enviado"
