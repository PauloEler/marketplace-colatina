"""Domínio isolado do MVP Encontre Quem Resolve."""

import re
import unicodedata
from urllib.parse import quote


URGENCY_OPTIONS = {
    "hoje": "Preciso hoje",
    "semana": "Nesta semana",
    "flexivel": "Posso esperar",
}

CATEGORY_KEYWORDS = {
    "Casa e manutenção": ("eletric", "encan", "pedreir", "pint", "telhad", "reparo"),
    "Tecnologia": ("celular", "computador", "internet", "notebook", "impressora"),
    "Transporte": ("carro", "moto", "frete", "mudanca", "guincho", "transporte"),
    "Saúde e bem-estar": ("saude", "medic", "dent", "fisi", "cuid", "beleza"),
    "Serviços profissionais": (
        "advog",
        "contador",
        "fotograf",
        "designer",
        "professor",
    ),
}


class ServiceRequestValidationError(ValueError):
    """Erro seguro para apresentar no formulário público."""


def _sem_acentos(valor):
    return "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", str(valor or ""))
        if not unicodedata.combining(caractere)
    ).lower()


def normalizar_whatsapp(valor):
    digitos = re.sub(r"\D", "", str(valor or ""))
    if digitos.startswith("55") and len(digitos) in {12, 13}:
        digitos = digitos[2:]
    if len(digitos) not in {10, 11}:
        raise ServiceRequestValidationError("Informe um WhatsApp com DDD válido.")
    return "55" + digitos


def inferir_categoria(problema):
    texto = _sem_acentos(problema)
    for categoria, palavras in CATEGORY_KEYWORDS.items():
        if any(palavra in texto for palavra in palavras):
            return categoria
    return "Outros serviços"


def validar_pedido(problema, bairro, urgencia, whatsapp):
    problema = re.sub(r"\s+", " ", str(problema or "")).strip()
    bairro = re.sub(r"\s+", " ", str(bairro or "")).strip()
    urgencia = str(urgencia or "").strip().lower()
    if len(problema) < 15:
        raise ServiceRequestValidationError(
            "Conte um pouco mais sobre o que você precisa resolver."
        )
    if len(problema) > 500:
        raise ServiceRequestValidationError(
            "Descreva o problema em no máximo 500 caracteres."
        )
    if re.search(r"(?:\D*\d){10,}", problema):
        raise ServiceRequestValidationError(
            "Não coloque telefone na descrição. Use somente o campo WhatsApp."
        )
    if len(bairro) < 2 or len(bairro) > 80:
        raise ServiceRequestValidationError("Informe um bairro válido de Colatina.")
    if urgencia not in URGENCY_OPTIONS:
        raise ServiceRequestValidationError("Escolha quando você precisa resolver.")
    return problema, bairro, urgencia, normalizar_whatsapp(whatsapp)


def criar_pedido(db, problema, bairro, urgencia, whatsapp, usuario_id=None):
    problema, bairro, urgencia, whatsapp = validar_pedido(
        problema, bairro, urgencia, whatsapp
    )
    cursor = db.execute(
        "INSERT INTO pedidos_servico "
        "(usuario_id, problema, categoria, bairro, urgencia, whatsapp) "
        "VALUES (?,?,?,?,?,?)",
        (usuario_id, problema, inferir_categoria(problema), bairro, urgencia, whatsapp),
    )
    db.commit()
    return getattr(cursor, "lastrowid", None)


def listar_pedidos_abertos(db):
    return db.execute(
        "SELECT id, problema, categoria, bairro, urgencia, respostas, criado_em "
        "FROM pedidos_servico WHERE status='aberto' "
        "ORDER BY CASE urgencia WHEN 'hoje' THEN 0 WHEN 'semana' THEN 1 ELSE 2 END, "
        "criado_em DESC, id DESC"
    ).fetchall()


def registrar_resposta(db, pedido_id):
    pedido = db.execute(
        "SELECT id, problema, whatsapp FROM pedidos_servico "
        "WHERE id=? AND status='aberto'",
        (pedido_id,),
    ).fetchone()
    if not pedido:
        return None
    db.execute(
        "UPDATE pedidos_servico SET respostas=respostas+1, "
        "atualizado_em=CURRENT_TIMESTAMP WHERE id=?",
        (pedido_id,),
    )
    db.commit()
    mensagem = (
        "Olá! Vi no Mercado Colatina que você precisa de ajuda com: "
        f"{pedido['problema']}. Posso conversar sobre isso?"
    )
    return f"https://wa.me/{pedido['whatsapp']}?text={quote(mensagem)}"
