"""Infraestrutura unica de notificacoes internas do Mercado Colatina."""

import json
from datetime import datetime


NOTIFICATION_TYPES = {
    "NOVO_PEDIDO",
    "NOVA_MENSAGEM",
    "ANUNCIO_APROVADO",
    "ANUNCIO_REPROVADO",
    "ANUNCIO_EXPIRANDO",
    "VENDA_CONCLUIDA",
    "AVISO_SISTEMA",
    "EMPRESA_PARCEIRA",
    "PROMOCAO",
}

NOTIFICATION_STATES = {"nao_lida", "lida", "arquivada"}

NOTIFICATION_ICONS = {
    "NOVO_PEDIDO": "package",
    "NOVA_MENSAGEM": "message",
    "ANUNCIO_APROVADO": "check",
    "ANUNCIO_REPROVADO": "alert",
    "ANUNCIO_EXPIRANDO": "clock",
    "VENDA_CONCLUIDA": "sale",
    "AVISO_SISTEMA": "info",
    "EMPRESA_PARCEIRA": "store",
    "PROMOCAO": "tag",
}


def criar_notificacao(
    db,
    usuario_id,
    tipo,
    titulo,
    descricao,
    url,
    *,
    referencia_tipo=None,
    referencia_id=None,
    chave_unica=None,
    dados=None,
):
    """Registra uma notificacao; chave_unica torna eventos repetidos idempotentes."""
    if tipo not in NOTIFICATION_TYPES:
        raise ValueError("Tipo de notificacao nao suportado.")
    if not titulo or not descricao or not url:
        raise ValueError("Titulo, descricao e URL sao obrigatorios.")
    db.execute(
        "INSERT INTO notifications "
        "(usuario_id, tipo, titulo, descricao, url, status, referencia_tipo, "
        "referencia_id, chave_unica, dados_json) VALUES (?,?,?,?,?,'nao_lida',?,?,?,?) "
        "ON CONFLICT (chave_unica) DO NOTHING",
        (
            usuario_id,
            tipo,
            titulo[:120],
            descricao[:280],
            url[:500],
            referencia_tipo,
            referencia_id,
            chave_unica,
            json.dumps(dados or {}, ensure_ascii=False, separators=(",", ":")),
        ),
    )


def destinatarios_da_loja(db, loja_id):
    """Inclui titular, gestores vinculados e administradores ativos."""
    return [
        linha["id"]
        for linha in db.execute(
            "SELECT DISTINCT u.id FROM usuarios u WHERE u.ativo=1 AND "
            "(u.id=? OR u.is_admin=1 OR EXISTS ("
            "SELECT 1 FROM loja_administradores la "
            "WHERE la.administrador_id=u.id AND la.loja_id=?))",
            (loja_id, loja_id),
        ).fetchall()
    ]


def listar_notificacoes(db, usuario_id, limite=8, incluir_arquivadas=False):
    filtro = "" if incluir_arquivadas else " AND status<>'arquivada'"
    return db.execute(
        "SELECT * FROM notifications WHERE usuario_id=?"
        + filtro
        + " ORDER BY criado_em DESC, id DESC LIMIT ?",
        (usuario_id, limite),
    ).fetchall()


def contar_nao_lidas(db, usuario_id):
    return db.execute(
        "SELECT COUNT(*) FROM notifications WHERE usuario_id=? AND status='nao_lida'",
        (usuario_id,),
    ).fetchone()[0]


def marcar_como_lida(db, notificacao_id, usuario_id):
    return db.execute(
        "UPDATE notifications SET status='lida', lida_em=CURRENT_TIMESTAMP "
        "WHERE id=? AND usuario_id=? AND status='nao_lida'",
        (notificacao_id, usuario_id),
    ).rowcount


def marcar_todas_como_lidas(db, usuario_id):
    return db.execute(
        "UPDATE notifications SET status='lida', lida_em=CURRENT_TIMESTAMP "
        "WHERE usuario_id=? AND status='nao_lida'",
        (usuario_id,),
    ).rowcount


def arquivar_notificacao(db, notificacao_id, usuario_id):
    return db.execute(
        "UPDATE notifications SET status='arquivada', "
        "arquivada_em=CURRENT_TIMESTAMP WHERE id=? AND usuario_id=?",
        (notificacao_id, usuario_id),
    ).rowcount


def buscar_notificacao(db, notificacao_id, usuario_id):
    return db.execute(
        "SELECT * FROM notifications WHERE id=? AND usuario_id=?",
        (notificacao_id, usuario_id),
    ).fetchone()


def estatisticas_administrativas(db):
    """Visao agregada; nao expoe o conteudo privado de outros usuarios."""
    resumo = db.execute(
        "SELECT COUNT(*) AS total, "
        "SUM(CASE WHEN status='nao_lida' THEN 1 ELSE 0 END) AS nao_lidas, "
        "SUM(CASE WHEN status='arquivada' THEN 1 ELSE 0 END) AS arquivadas, "
        "COUNT(DISTINCT usuario_id) AS usuarios FROM notifications"
    ).fetchone()
    por_tipo = db.execute(
        "SELECT tipo, COUNT(*) AS total FROM notifications "
        "GROUP BY tipo ORDER BY total DESC, tipo"
    ).fetchall()
    return {"resumo": resumo, "por_tipo": por_tipo}


def formatar_data_notificacao(valor):
    if not valor:
        return ""
    if isinstance(valor, datetime):
        data = valor
    else:
        try:
            data = datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
        except ValueError:
            return str(valor)
    return data.strftime("%d/%m/%Y às %H:%M")
