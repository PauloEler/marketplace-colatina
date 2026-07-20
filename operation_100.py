"""Indicadores executivos da Operacao Primeiros 100.

As consultas sao somente leitura e reutilizam a coleta minimizada da Operacao
Tracao. Nenhum valor sem fonte oficial e estimado.
"""

from datetime import datetime, timedelta, timezone

from affiliate_analytics import COLATINA_TZ
from community_intelligence import construir_inteligencia_comunidade
from traction_metrics import build_traction_dashboard


OPERATION_100_TARGET = 100


def _utc_text(value):
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _ids(rows):
    return {int(row[0]) for row in rows}


def _conversion(current, previous):
    if not previous:
        return None
    return round(current * 100 / previous, 1)


def _funnel_step(key, label, value, previous=None, source=""):
    conversion = _conversion(value, previous) if previous is not None else None
    return {
        "key": key,
        "label": label,
        "value": value,
        "conversion": conversion,
        "conversion_label": (
            f"{conversion:.1f}%" if conversion is not None else "Aguardando base"
        ),
        "source": source,
    }


def _growth_funnel(db, now):
    local_now = now.astimezone(COLATINA_TZ)
    cohort_start = local_now - timedelta(days=29)
    current_week = local_now.date() - timedelta(days=6)
    previous_week = current_week - timedelta(days=7)
    previous_end = current_week - timedelta(days=1)

    visits = db.execute(
        "SELECT COALESCE(SUM(visits),0) FROM traction_access_source_daily "
        "WHERE access_date>=?",
        (str(cohort_start.date()),),
    ).fetchone()[0]
    registered = _ids(
        db.execute(
            "SELECT id FROM usuarios WHERE is_admin=0 AND criado_em>=?",
            (_utc_text(cohort_start),),
        ).fetchall()
    )
    first_ad = registered & _ids(
        db.execute("SELECT DISTINCT usuario_id FROM anuncios").fetchall()
    )
    order_participants = _ids(
        db.execute(
            "SELECT comprador_id FROM pedidos UNION SELECT vendedor_id FROM pedidos"
        ).fetchall()
    )
    first_order = first_ad & order_participants
    sellers = _ids(
        db.execute(
            "SELECT DISTINCT vendedor_id FROM pedidos WHERE status='concluido'"
        ).fetchall()
    )
    first_sale = first_order & sellers
    activity = db.execute(
        "SELECT user_id, activity_date FROM traction_user_activity_daily "
        "WHERE activity_date>=?",
        (str(previous_week),),
    ).fetchall()
    current_users = {
        int(row[0]) for row in activity if str(row[1])[:10] >= str(current_week)
    }
    previous_users = {
        int(row[0])
        for row in activity
        if str(previous_week) <= str(row[1])[:10] <= str(previous_end)
    }
    recurring = first_sale & current_users & previous_users

    steps = [
        _funnel_step(
            "visitor",
            "Visitante",
            int(visits or 0),
            source="visitas agregadas nos ultimos 30 dias",
        ),
        _funnel_step(
            "registration",
            "Cadastro",
            len(registered),
            int(visits or 0),
            "contas nao administrativas criadas nos ultimos 30 dias",
        ),
        _funnel_step(
            "first_ad",
            "Primeiro anuncio",
            len(first_ad),
            len(registered),
            "pessoas da coorte que publicaram anuncio",
        ),
        _funnel_step(
            "first_order",
            "Primeiro pedido",
            len(first_order),
            len(first_ad),
            "anunciantes da coorte envolvidos em pedido",
        ),
        _funnel_step(
            "first_sale",
            "Primeira venda",
            len(first_sale),
            len(first_order),
            "participantes da etapa anterior com venda concluida",
        ),
        _funnel_step(
            "recurring",
            "Usuario recorrente",
            len(recurring),
            len(first_sale),
            "participantes da etapa anterior ativos em duas semanas consecutivas",
        ),
    ]
    return {
        "window": "Ultimos 30 dias",
        "steps": steps,
        "note": (
            "Visitantes sao agregados. Da etapa Cadastro em diante, o funil e uma "
            "coorte progressiva para preservar comparabilidade entre as etapas."
        ),
    }


def _companies(db, partners):
    registered_ids = _ids(
        db.execute(
            "SELECT id FROM usuarios WHERE ativo=1 AND TRIM(COALESCE(loja_nome,''))<>''"
        ).fetchall()
    )
    active_ids = registered_ids & _ids(
        db.execute(
            "SELECT DISTINCT usuario_id FROM anuncios "
            "WHERE ativo=1 AND excluido_em IS NULL"
        ).fetchall()
    )
    partner_count = sum(1 for item in partners if not item.get("placeholder"))
    return {
        "invited": None,
        "invited_label": "Nao mensurado",
        "registered": len(registered_ids),
        "partners": partner_count,
        "active": len(active_ids),
        "without_ads": len(registered_ids - active_ids),
        "without_ads_definition": "empresa cadastrada sem anuncio ativo",
    }


def _community(db, now):
    intelligence = construir_inteligencia_comunidade(db, now)
    return {
        "total": intelligence["total"],
        "categories": intelligence["ranking_categorias"],
        "trends": intelligence["categorias_crescimento"],
        "implemented": intelligence["implementadas"],
        "pending": intelligence["pendentes"],
        "radar": intelligence["resposta_cidade"],
    }


def _milestones(recurring, companies, community):
    return [
        {
            "label": "Primeiro usuario recorrente",
            "done": recurring >= 1,
            "automatic": True,
        },
        {
            "label": "Primeiros 10 usuarios recorrentes",
            "done": recurring >= 10,
            "automatic": True,
        },
        {
            "label": "Primeiros 50 usuarios recorrentes",
            "done": recurring >= 50,
            "automatic": True,
        },
        {
            "label": "Primeiros 100 usuarios recorrentes",
            "done": recurring >= 100,
            "automatic": True,
        },
        {
            "label": "Primeira empresa parceira",
            "done": companies["partners"] >= 1,
            "automatic": True,
        },
        {
            "label": "Primeira comissao dos afiliados",
            "done": False,
            "automatic": False,
            "note": "Aguardando fonte oficial do parceiro",
        },
        {
            "label": "Primeira sugestao implementada",
            "done": community["implemented"] >= 1,
            "automatic": True,
        },
        {
            "label": "Primeira campanha comunitaria",
            "done": False,
            "automatic": False,
            "note": "Ainda sem fonte oficial de registro",
        },
    ]


def _blockers(data):
    blockers = []
    if data["users"]["recurring"] == 0:
        blockers.append("Ainda nao ha usuario ativo em duas semanas consecutivas.")
    if data["funnel"]["steps"][0]["value"] == 0:
        blockers.append(
            "A base agregada de visitantes dos ultimos 30 dias ainda esta vazia."
        )
    if data["companies"]["without_ads"]:
        blockers.append(
            f"{data['companies']['without_ads']} empresa(s) cadastrada(s) esta(ao) sem anuncio ativo."
        )
    if data["affiliates"]["revenue"] is None:
        blockers.append(
            "A receita de afiliados ainda nao possui retorno oficial no sistema."
        )
    if not data["community"]["radar"]["conclusiva"]:
        blockers.append("O Radar da Cidade ainda nao possui amostra conclusiva.")
    return blockers or ["Nenhum bloqueio mensuravel identificado neste momento."]


def build_operation_100_dashboard(db, offers, partners, now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    traction = build_traction_dashboard(db, offers, partners, now)
    total_users = db.execute(
        "SELECT COUNT(*) FROM usuarios WHERE is_admin=0"
    ).fetchone()[0]
    total_orders = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    companies = _companies(db, partners)
    community = _community(db, now)
    funnel = _growth_funnel(db, now)
    recurring = traction["users"]["recorrentes"]
    data = {
        "generated_at": now.astimezone(COLATINA_TZ).strftime("%d/%m/%Y - %H:%M"),
        "target": OPERATION_100_TARGET,
        "progress": min(100, round(recurring * 100 / OPERATION_100_TARGET)),
        "users": {
            "registered": total_users,
            "active": traction["users"]["ativos_7_dias"],
            "recurring": recurring,
        },
        "companies": companies,
        "marketplace": {
            "active_ads": traction["marketplace"]["anuncios_ativos"],
            "orders": total_orders,
            "average_response": traction["marketplace"]["tempo_medio_resposta"],
        },
        "affiliates": {
            "clicks": traction["affiliates"]["cliques_30_dias"],
            "revenue": traction["affiliates"]["receita"],
            "revenue_label": traction["affiliates"]["receita_rotulo"],
        },
        "community": community,
        "funnel": funnel,
    }
    data["milestones"] = _milestones(recurring, companies, community)
    data["blockers"] = _blockers(data)
    return data
