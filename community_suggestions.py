"""Domínio isolado para escuta e gestão de sugestões da comunidade."""

from datetime import datetime


SUGGESTION_CATEGORIES = {
    "comercio": "Comércio",
    "empresas": "Empresas",
    "empregos": "Empregos",
    "eventos": "Eventos",
    "saude": "Saúde",
    "seguranca": "Segurança",
    "mobilidade": "Mobilidade",
    "marketplace": "Marketplace",
    "cidade": "Cidade",
    "outros": "Outros",
}

SUGGESTION_STATUSES = {
    "nova": "Nova",
    "em_analise": "Em análise",
    "planejada": "Planejada",
    "implementada": "Implementada",
    "arquivada": "Arquivada",
}


class SuggestionValidationError(ValueError):
    """Erro seguro para apresentar no formulário público."""


def validar_sugestao(nome, categoria, mensagem):
    nome = str(nome or "").strip()
    categoria = str(categoria or "").strip().lower()
    mensagem = str(mensagem or "").strip()

    if len(nome) > 80:
        raise SuggestionValidationError("O nome deve ter no máximo 80 caracteres.")
    if categoria not in SUGGESTION_CATEGORIES:
        raise SuggestionValidationError("Escolha uma categoria válida.")
    if len(mensagem) < 10:
        raise SuggestionValidationError(
            "Conte um pouco mais sobre o que está faltando em Colatina."
        )
    if len(mensagem) > 2000:
        raise SuggestionValidationError(
            "A mensagem deve ter no máximo 2.000 caracteres."
        )
    return nome, categoria, mensagem


def criar_sugestao(db, nome, categoria, mensagem):
    nome, categoria, mensagem = validar_sugestao(nome, categoria, mensagem)
    cursor = db.execute(
        "INSERT INTO sugestoes_comunidade (nome, categoria, mensagem) VALUES (?,?,?)",
        (nome or None, categoria, mensagem),
    )
    db.commit()
    return getattr(cursor, "lastrowid", None)


def listar_sugestoes(db, status="todos", categoria="todas"):
    filtros = []
    parametros = []
    if status in SUGGESTION_STATUSES:
        filtros.append("status=?")
        parametros.append(status)
    if categoria in SUGGESTION_CATEGORIES:
        filtros.append("categoria=?")
        parametros.append(categoria)
    where = " WHERE " + " AND ".join(filtros) if filtros else ""
    return db.execute(
        "SELECT * FROM sugestoes_comunidade"
        + where
        + " ORDER BY criado_em DESC, id DESC",
        tuple(parametros),
    ).fetchall()


def atualizar_status_sugestao(db, sugestao_id, novo_status):
    if novo_status not in SUGGESTION_STATUSES:
        raise SuggestionValidationError("Escolha um status válido.")
    existente = db.execute(
        "SELECT id FROM sugestoes_comunidade WHERE id=?", (sugestao_id,)
    ).fetchone()
    if not existente:
        return False
    db.execute(
        "UPDATE sugestoes_comunidade SET status=?, "
        "analisada_em=CASE WHEN ?<>'nova' THEN "
        "COALESCE(analisada_em, CURRENT_TIMESTAMP) ELSE analisada_em END, "
        "implementada_em=CASE WHEN ?='implementada' THEN "
        "COALESCE(implementada_em, CURRENT_TIMESTAMP) ELSE implementada_em END, "
        "atualizado_em=CURRENT_TIMESTAMP WHERE id=?",
        (novo_status, novo_status, novo_status, sugestao_id),
    )
    db.commit()
    return True


def _data_hora(valor):
    if not valor:
        return None
    if isinstance(valor, datetime):
        return valor
    try:
        return datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
    except ValueError:
        return None


def formatar_data_sugestao(valor):
    data = _data_hora(valor)
    return data.strftime("%d/%m/%Y às %H:%M") if data else str(valor or "")


def _formatar_tempo_medio(minutos):
    if minutos is None:
        return "Sem dados"
    minutos = max(0, round(minutos))
    if minutos < 60:
        return f"{minutos} min"
    horas, minutos_restantes = divmod(minutos, 60)
    if horas < 24:
        return f"{horas} h" + (f" {minutos_restantes} min" if minutos_restantes else "")
    dias, horas_restantes = divmod(horas, 24)
    return f"{dias} d" + (f" {horas_restantes} h" if horas_restantes else "")


def construir_metricas_sugestoes(db):
    sugestoes = db.execute(
        "SELECT categoria, status, criado_em, analisada_em FROM sugestoes_comunidade"
    ).fetchall()
    categorias = {chave: 0 for chave in SUGGESTION_CATEGORIES}
    status = {chave: 0 for chave in SUGGESTION_STATUSES}
    tempos_analise = []

    for sugestao in sugestoes:
        if sugestao["categoria"] in categorias:
            categorias[sugestao["categoria"]] += 1
        if sugestao["status"] in status:
            status[sugestao["status"]] += 1
        criada_em = _data_hora(sugestao["criado_em"])
        analisada_em = _data_hora(sugestao["analisada_em"])
        if criada_em and analisada_em:
            tempos_analise.append((analisada_em - criada_em).total_seconds() / 60)

    ranking = [
        {
            "chave": chave,
            "categoria": SUGGESTION_CATEGORIES[chave],
            "total": total,
        }
        for chave, total in categorias.items()
        if total
    ]
    ranking.sort(key=lambda item: (-item["total"], item["categoria"]))
    media = sum(tempos_analise) / len(tempos_analise) if tempos_analise else None
    return {
        "total": len(sugestoes),
        "implementadas": status["implementada"],
        "tempo_medio_analise": _formatar_tempo_medio(media),
        "por_status": status,
        "ranking_categorias": ranking,
        "categoria_principal": ranking[0] if ranking else None,
    }
