"""Métricas determinísticas e minimizadas da Operação Tração."""

import re
import unicodedata
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

from affiliate_analytics import COLATINA_TZ, build_affiliate_dashboard
from community_intelligence import construir_inteligencia_comunidade


TRACTION_START_DATE = date(2026, 7, 20)
TRACTION_END_DATE = TRACTION_START_DATE + timedelta(days=29)
KNOWN_ACCESS_SOURCES = (
    "direto",
    "google",
    "facebook",
    "instagram",
    "whatsapp",
    "email",
    "outros",
)
SOURCE_LABELS = {
    "direto": "Acesso direto",
    "google": "Google",
    "facebook": "Facebook",
    "instagram": "Instagram",
    "whatsapp": "WhatsApp",
    "email": "E-mail",
    "outros": "Outras origens",
}


def _sem_acento(value):
    normalized = unicodedata.normalize("NFKD", str(value or "").lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _source_key(value):
    value = _sem_acento(value)
    value = re.sub(r"[^a-z0-9]+", "", value)
    aliases = {
        "googleads": "google",
        "googlebusiness": "google",
        "googlemaps": "google",
        "fb": "facebook",
        "meta": "facebook",
        "ig": "instagram",
        "wa": "whatsapp",
        "newsletter": "email",
    }
    value = aliases.get(value, value)
    return value if value in KNOWN_ACCESS_SOURCES else "outros"


def classify_access_source(referrer="", utm_source=""):
    """Classifica a origem sem persistir URL, domínio ou parâmetros brutos."""
    if str(utm_source or "").strip():
        return _source_key(utm_source)
    hostname = (urlparse(str(referrer or "")).hostname or "").lower()
    if not hostname:
        return "direto"
    if "google." in hostname:
        return "google"
    if "facebook." in hostname or hostname.endswith("fb.com"):
        return "facebook"
    if "instagram." in hostname:
        return "instagram"
    if "whatsapp." in hostname or hostname.endswith("wa.me"):
        return "whatsapp"
    return "outros"


def record_access_source(db, source, activity_date=None):
    activity_date = str(activity_date or datetime.now(COLATINA_TZ).date())
    source = source if source in KNOWN_ACCESS_SOURCES else "outros"
    db.execute(
        "INSERT INTO traction_access_source_daily "
        "(access_date,source,visits) VALUES (?,?,1) "
        "ON CONFLICT(access_date,source) DO UPDATE SET "
        "visits=traction_access_source_daily.visits+1",
        (activity_date, source),
    )


def record_user_activity(db, user_id, activity_date=None):
    activity_date = str(activity_date or datetime.now(COLATINA_TZ).date())
    db.execute(
        "INSERT INTO traction_user_activity_daily "
        "(user_id,activity_date,sessions) VALUES (?,?,1) "
        "ON CONFLICT(user_id,activity_date) DO UPDATE SET "
        "sessions=traction_user_activity_daily.sessions+1, "
        "last_seen_at=CURRENT_TIMESTAMP",
        (user_id, activity_date),
    )


def _timestamp(value):
    if not value:
        return None
    if isinstance(value, datetime):
        result = value
    else:
        try:
            result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
    if result.tzinfo:
        result = result.astimezone(timezone.utc).replace(tzinfo=None)
    return result


def _utc_text(value):
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _format_duration(minutes):
    if minutes is None:
        return "Aguardando dados"
    minutes = max(0, round(minutes))
    if minutes < 60:
        return f"{minutes} min"
    hours, remainder = divmod(minutes, 60)
    if hours < 24:
        return f"{hours} h" + (f" {remainder} min" if remainder else "")
    days, hours = divmod(hours, 24)
    return f"{days} d" + (f" {hours} h" if hours else "")


def _format_currency(value):
    value = value.quantize(Decimal("0.01"))
    formatted = f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatted}"


def _decimal_sum(rows, key):
    total = Decimal("0")
    for row in rows:
        try:
            total += Decimal(str(row[key] or "0").replace(",", "."))
        except InvalidOperation:
            continue
    return total


def _period_context(now):
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)
    local_now = now.astimezone(COLATINA_TZ)
    current_start_date = local_now.date() - timedelta(days=6)
    previous_start_date = current_start_date - timedelta(days=7)
    previous_end_date = current_start_date - timedelta(days=1)
    current_start_local = datetime.combine(
        current_start_date, datetime.min.time(), tzinfo=COLATINA_TZ
    )
    month_start_local = datetime.combine(
        local_now.date() - timedelta(days=29),
        datetime.min.time(),
        tzinfo=COLATINA_TZ,
    )
    return {
        "now": now,
        "local_now": local_now,
        "current_start_date": current_start_date,
        "previous_start_date": previous_start_date,
        "previous_end_date": previous_end_date,
        "current_start_utc": _utc_text(current_start_local),
        "month_start_utc": _utc_text(month_start_local),
    }


def _user_metrics(db, period):
    new_users = db.execute(
        "SELECT COUNT(*) FROM usuarios WHERE is_admin=0 AND criado_em>=?",
        (period["current_start_utc"],),
    ).fetchone()[0]
    rows = db.execute(
        "SELECT a.user_id, a.activity_date FROM traction_user_activity_daily a "
        "JOIN usuarios u ON u.id=a.user_id "
        "WHERE u.is_admin=0 AND u.ativo=1 AND a.activity_date>=?",
        (str(period["previous_start_date"]),),
    ).fetchall()
    current_users = {
        row["user_id"]
        for row in rows
        if str(row["activity_date"])[:10] >= str(period["current_start_date"])
    }
    previous_users = {
        row["user_id"]
        for row in rows
        if str(period["previous_start_date"])
        <= str(row["activity_date"])[:10]
        <= str(period["previous_end_date"])
    }
    recurring = current_users & previous_users
    return_rate = (
        round(len(recurring) * 100 / len(previous_users), 1) if previous_users else None
    )
    return {
        "novos_7_dias": new_users,
        "ativos_7_dias": len(current_users),
        "recorrentes": len(recurring),
        "retorno_semanal": return_rate,
        "retorno_rotulo": (
            f"{return_rate:.1f}%" if return_rate is not None else "Aguardando base"
        ),
        "base_anterior": len(previous_users),
    }


def _access_sources(db, period):
    rows = db.execute(
        "SELECT source, SUM(visits) AS total FROM traction_access_source_daily "
        "WHERE access_date>=? GROUP BY source",
        (str(period["current_start_date"]),),
    ).fetchall()
    totals = {row["source"]: int(row["total"] or 0) for row in rows}
    result = [
        {"source": key, "label": SOURCE_LABELS[key], "total": totals.get(key, 0)}
        for key in KNOWN_ACCESS_SOURCES
        if totals.get(key, 0)
    ]
    result.sort(key=lambda item: (-item["total"], item["label"]))
    return result


def _company_metrics(db, local_partners):
    registered = db.execute(
        "SELECT COUNT(*) FROM usuarios WHERE ativo=1 "
        "AND TRIM(COALESCE(loja_nome,''))<>''"
    ).fetchone()[0]
    active = db.execute(
        "SELECT COUNT(DISTINCT u.id) FROM usuarios u JOIN anuncios a "
        "ON a.usuario_id=u.id WHERE u.ativo=1 AND a.ativo=1 "
        "AND TRIM(COALESCE(u.loja_nome,''))<>''"
    ).fetchone()[0]
    partners = sum(1 for partner in local_partners if not partner.get("placeholder"))
    return {
        "convidadas": None,
        "convidadas_rotulo": "Não mensurado",
        "cadastradas": registered,
        "parceiras": partners,
        "ativas": active,
    }


def _marketplace_metrics(db, period):
    active_ads = db.execute(
        "SELECT COUNT(*) FROM anuncios WHERE ativo=1 AND excluido_em IS NULL"
    ).fetchone()[0]
    published = db.execute(
        "SELECT COUNT(*) FROM anuncios WHERE criado_em>=?",
        (period["current_start_utc"],),
    ).fetchone()[0]
    orders_7 = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE criado_em>=?",
        (period["current_start_utc"],),
    ).fetchone()[0]
    orders_30 = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE criado_em>=?",
        (period["month_start_utc"],),
    ).fetchone()[0]
    concluded_30 = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status='concluido' AND criado_em>=?",
        (period["month_start_utc"],),
    ).fetchone()[0]
    conversion = round(concluded_30 * 100 / orders_30, 1) if orders_30 else 0.0
    responses = db.execute(
        "SELECT p.criado_em, MIN(e.criado_em) AS respondido_em FROM pedidos p "
        "JOIN pedido_eventos e ON e.pedido_id=p.id "
        "WHERE p.criado_em>=? AND e.tipo='VENDEDOR_CONFIRMOU' "
        "GROUP BY p.id, p.criado_em",
        (period["month_start_utc"],),
    ).fetchall()
    response_minutes = []
    for row in responses:
        created = _timestamp(row["criado_em"])
        responded = _timestamp(row["respondido_em"])
        if created and responded:
            response_minutes.append(max(0, (responded - created).total_seconds() / 60))
    average_response = (
        sum(response_minutes) / len(response_minutes) if response_minutes else None
    )
    commissions = db.execute(
        "SELECT comissao FROM pedidos WHERE pagamento_status='aprovado'"
    ).fetchall()
    platform_revenue = _decimal_sum(commissions, "comissao")
    return {
        "anuncios_ativos": active_ads,
        "anuncios_publicados_7_dias": published,
        "pedidos_7_dias": orders_7,
        "pedidos_30_dias": orders_30,
        "pedidos_concluidos_30_dias": concluded_30,
        "conversao": conversion,
        "conversao_rotulo": f"{conversion:.1f}%",
        "tempo_medio_resposta": _format_duration(average_response),
        "respostas_observadas": len(response_minutes),
        "receita_plataforma": platform_revenue,
        "receita_plataforma_rotulo": _format_currency(platform_revenue),
    }


def _affiliate_metrics(db, offers, period):
    analytics = build_affiliate_dashboard(db, offers, period["now"])
    previous_start = _utc_text(period["now"] - timedelta(days=14))
    current_start = _utc_text(period["now"] - timedelta(days=7))
    previous_clicks = db.execute(
        "SELECT COUNT(*) FROM afiliado_eventos WHERE tipo_evento='click' "
        "AND ocorrido_em>=? AND ocorrido_em<?",
        (previous_start, current_start),
    ).fetchone()[0]
    current_clicks = analytics["clicks_7_days"]
    trend = current_clicks - previous_clicks
    impressions = sum(item["impressions"] for item in analytics["ranking"])
    clicks = analytics["clicks_30_days"]
    ctr = round(clicks * 100 / impressions, 2) if impressions else 0.0
    return {
        "cliques_7_dias": current_clicks,
        "cliques_30_dias": clicks,
        "impressoes_30_dias": impressions,
        "ctr": ctr,
        "ctr_rotulo": f"{ctr:.2f}%",
        "categoria_top": (
            analytics["top_category"]["category"]
            if analytics["top_category"]
            else "Aguardando cliques"
        ),
        "tendencia": trend,
        "tendencia_rotulo": f"{trend:+d}",
        "receita": None,
        "receita_rotulo": "Não informada pelo parceiro",
        "ranking": analytics["ranking"],
    }


def _community_metrics(db, period):
    intelligence = construir_inteligencia_comunidade(db, period["now"])
    current = db.execute(
        "SELECT COUNT(*) FROM sugestoes_comunidade WHERE criado_em>=?",
        (period["current_start_utc"],),
    ).fetchone()[0]
    previous_start = _utc_text(period["now"] - timedelta(days=14))
    previous = db.execute(
        "SELECT COUNT(*) FROM sugestoes_comunidade WHERE criado_em>=? AND criado_em<?",
        (previous_start, period["current_start_utc"]),
    ).fetchone()[0]
    top_category = (
        intelligence["ranking_categorias"][0]["categoria"]
        if intelligence["ranking_categorias"]
        else "Aguardando sugestões"
    )
    return {
        "total": intelligence["total"],
        "recebidas_7_dias": current,
        "participacao_anterior": previous,
        "variacao_semanal": current - previous,
        "implementadas": intelligence["implementadas"],
        "categoria_top": top_category,
        "radar": intelligence["resposta_cidade"],
    }


def build_traction_dashboard(db, offers, local_partners, now=None):
    now = now or datetime.now(timezone.utc)
    period = _period_context(now)
    local_today = period["local_now"].date()
    elapsed = max(0, min(30, (local_today - TRACTION_START_DATE).days + 1))
    remaining = max(0, (TRACTION_END_DATE - local_today).days)
    users = _user_metrics(db, period)
    companies = _company_metrics(db, local_partners)
    marketplace = _marketplace_metrics(db, period)
    affiliates = _affiliate_metrics(db, offers, period)
    community = _community_metrics(db, period)
    sources = _access_sources(db, period)
    gaps = []
    if users["base_anterior"] == 0:
        gaps.append(
            "Retorno semanal aguarda uma semana anterior com atividade registrada."
        )
    if not sources:
        gaps.append("Origem do acesso começará a formar base após a publicação.")
    gaps.append("Empresas convidadas ainda não possuem uma fonte oficial de registro.")
    gaps.append("Receita de afiliados não é informada pelo parceiro ao sistema.")
    return {
        "version": "1.0",
        "generated_at": period["local_now"].strftime("%d/%m/%Y · %H:%M"),
        "start_date": TRACTION_START_DATE.strftime("%d/%m/%Y"),
        "end_date": TRACTION_END_DATE.strftime("%d/%m/%Y"),
        "elapsed_days": elapsed,
        "remaining_days": remaining,
        "users": users,
        "access_sources": sources,
        "companies": companies,
        "marketplace": marketplace,
        "affiliates": affiliates,
        "community": community,
        "gaps": gaps,
    }


def _next_week_mission(data):
    if data["users"]["ativos_7_dias"] == 0:
        return "Atrair os primeiros usuários da semana e medir a origem dos acessos."
    if data["users"]["base_anterior"] == 0:
        return "Formar a primeira base comparável de retorno semanal."
    if data["companies"]["ativas"] == 0:
        return "Ativar a primeira empresa com anúncio disponível."
    return "Aumentar retorno semanal sem reduzir confiança ou qualidade dos anúncios."


def render_weekly_report(data):
    problems = data["gaps"] or ["Nenhum problema crítico identificado nos dados."]
    opportunities = [
        f"Categoria de afiliados com maior interesse: {data['affiliates']['categoria_top']}.",
        f"Categoria mais sugerida pela comunidade: {data['community']['categoria_top']}.",
        f"Existem {data['companies']['ativas']} empresas com anúncios ativos.",
    ]
    suggestions = [
        "Usar links com UTM nas campanhas para melhorar a leitura de origem.",
        "Convidar empresas com uma proposta simples e registrar o resultado semanal.",
        "Revisar os indicadores toda segunda-feira antes de aprovar nova funcionalidade.",
    ]
    lines = [
        "# RELATÓRIO EXECUTIVO SEMANAL",
        "",
        f"**Gerado em:** {data['generated_at']}",
        "**Operação:** Tração 1.0",
        "",
        "## Resumo da semana",
        "",
        (
            f"A semana registrou {data['users']['novos_7_dias']} novos usuários, "
            f"{data['users']['recorrentes']} usuários recorrentes, "
            f"{data['marketplace']['anuncios_publicados_7_dias']} anúncios publicados, "
            f"{data['marketplace']['pedidos_7_dias']} pedidos, "
            f"{data['affiliates']['cliques_7_dias']} cliques de afiliados e "
            f"{data['community']['recebidas_7_dias']} sugestões da comunidade."
        ),
        "",
        "## Indicadores",
        "",
        f"- Usuários recorrentes: {data['users']['recorrentes']}",
        f"- Retorno semanal: {data['users']['retorno_rotulo']}",
        f"- Empresas cadastradas: {data['companies']['cadastradas']}",
        f"- Empresas ativas: {data['companies']['ativas']}",
        f"- Anúncios ativos: {data['marketplace']['anuncios_ativos']}",
        f"- Conversão de pedidos em 30 dias: {data['marketplace']['conversao_rotulo']}",
        f"- Receita da plataforma: {data['marketplace']['receita_plataforma_rotulo']}",
        f"- Cliques de afiliados em 30 dias: {data['affiliates']['cliques_30_dias']}",
        f"- Receita de afiliados: {data['affiliates']['receita_rotulo']}",
        f"- Sugestões recebidas: {data['community']['total']}",
        "",
        "## Problemas encontrados",
        "",
        *[f"- {item}" for item in problems],
        "",
        "## Oportunidades",
        "",
        *[f"- {item}" for item in opportunities],
        "",
        "## Sugestões",
        "",
        *[f"- {item}" for item in suggestions],
        "",
        "## Missão da próxima semana",
        "",
        _next_week_mission(data),
        "",
    ]
    return "\n".join(lines)
