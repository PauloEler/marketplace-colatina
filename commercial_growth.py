"""Operacao comercial minima para conquistar Colatina bairro por bairro."""

from datetime import datetime, timedelta, timezone

from affiliate_analytics import COLATINA_TZ


MISSION_METRICS = {
    "empresas_visitadas": "Empresas visitadas",
    "empresas_interessadas": "Empresas interessadas",
    "empresas_cadastradas": "Empresas cadastradas",
    "novos_anuncios": "Novos anuncios",
    "bairros_visitados": "Bairros visitados",
}


class CommercialGrowthValidationError(ValueError):
    """Erro de validacao seguro para a interface administrativa."""


def _text(value, field, minimum, maximum, optional=False):
    value = str(value or "").strip()
    if optional and not value:
        return ""
    if not minimum <= len(value) <= maximum:
        raise CommercialGrowthValidationError(
            f"{field} deve ter entre {minimum} e {maximum} caracteres."
        )
    return value


def _integer(value, field, minimum=0, maximum=10000):
    try:
        value = int(value)
    except (TypeError, ValueError) as exc:
        raise CommercialGrowthValidationError(
            f"{field} deve ser um numero inteiro."
        ) from exc
    if not minimum <= value <= maximum:
        raise CommercialGrowthValidationError(
            f"{field} deve estar entre {minimum} e {maximum}."
        )
    return value


def _flag(value):
    return 1 if str(value or "").lower() in {"1", "true", "on", "sim"} else 0


def _local_period(now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    local_now = now.astimezone(COLATINA_TZ)
    week_start_date = local_now.date() - timedelta(days=local_now.weekday())
    week_end_date = week_start_date + timedelta(days=6)
    week_start_local = datetime.combine(
        week_start_date, datetime.min.time(), tzinfo=COLATINA_TZ
    )
    week_end_local = datetime.combine(
        week_end_date + timedelta(days=1), datetime.min.time(), tzinfo=COLATINA_TZ
    )
    return {
        "now": now,
        "local_now": local_now,
        "start_date": week_start_date,
        "end_date": week_end_date,
        "start_utc": week_start_local.astimezone(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "end_utc": week_end_local.astimezone(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }


def create_company(db, name, contact, neighborhood, visits, interested, created_by):
    name = _text(name, "Nome da empresa", 2, 120)
    contact = _text(contact, "Contato", 2, 120, optional=True)
    neighborhood = _text(neighborhood, "Bairro", 2, 80)
    visits = _integer(visits, "Visitas realizadas", 1, 999)
    existing = db.execute(
        "SELECT id FROM growth_commercial_companies WHERE lower(name)=lower(?)",
        (name,),
    ).fetchone()
    if existing:
        raise CommercialGrowthValidationError("Esta empresa ja esta no painel.")
    db.execute(
        "INSERT INTO growth_commercial_companies "
        "(name,contact,neighborhood,visits_count,interested,created_by) "
        "VALUES (?,?,?,?,?,?)",
        (name, contact, neighborhood, visits, _flag(interested), created_by),
    )
    db.commit()


def update_company_checklist(db, company_id, values):
    existing = db.execute(
        "SELECT id FROM growth_commercial_companies WHERE id=?", (company_id,)
    ).fetchone()
    if not existing:
        return False
    visits = _integer(values.get("visits_count"), "Visitas realizadas", 1, 999)
    db.execute(
        "UPDATE growth_commercial_companies SET visits_count=?, interested=?, "
        "registered=?, ad_published=?, first_order=?, partner=?, referred_other=?, "
        "updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (
            visits,
            _flag(values.get("interested")),
            _flag(values.get("registered")),
            _flag(values.get("ad_published")),
            _flag(values.get("first_order")),
            _flag(values.get("partner")),
            _flag(values.get("referred_other")),
            company_id,
        ),
    )
    db.commit()
    return True


def list_companies(db):
    return db.execute(
        "SELECT * FROM growth_commercial_companies ORDER BY updated_at DESC, id DESC"
    ).fetchall()


def create_ambassador(
    db, name, contact, neighborhood, companies_referred, users_referred, participation
):
    name = _text(name, "Nome", 2, 100)
    contact = _text(contact, "Contato", 5, 120)
    neighborhood = _text(neighborhood, "Bairro", 2, 80)
    companies_referred = _integer(companies_referred, "Empresas indicadas", 0, 10000)
    users_referred = _integer(users_referred, "Usuarios indicados", 0, 10000)
    participation = _text(participation, "Participacao", 2, 240)
    db.execute(
        "INSERT INTO growth_ambassadors "
        "(name,contact,neighborhood,companies_referred,users_referred,participation) "
        "VALUES (?,?,?,?,?,?)",
        (
            name,
            contact,
            neighborhood,
            companies_referred,
            users_referred,
            participation,
        ),
    )
    db.commit()


def list_ambassadors(db):
    return db.execute(
        "SELECT * FROM growth_ambassadors WHERE active=1 "
        "ORDER BY companies_referred DESC, users_referred DESC, name"
    ).fetchall()


def create_weekly_mission(db, title, metric, target, created_by, now=None):
    title = _text(title, "Missao", 5, 160)
    if metric not in MISSION_METRICS:
        raise CommercialGrowthValidationError("Escolha um indicador valido.")
    target = _integer(target, "Meta", 1, 10000)
    period = _local_period(now)
    db.execute("UPDATE growth_weekly_missions SET active=0 WHERE active=1")
    db.execute(
        "INSERT INTO growth_weekly_missions "
        "(title,metric,target,week_start,week_end,active,created_by) "
        "VALUES (?,?,?,?,?,1,?)",
        (
            title,
            metric,
            target,
            str(period["start_date"]),
            str(period["end_date"]),
            created_by,
        ),
    )
    db.commit()


def _weekly_counts(db, period):
    params = (period["start_utc"], period["end_utc"])
    companies = db.execute(
        "SELECT * FROM growth_commercial_companies "
        "WHERE created_at>=? AND created_at<?",
        params,
    ).fetchall()
    users = db.execute(
        "SELECT COUNT(*) FROM usuarios WHERE is_admin=0 AND criado_em>=? AND criado_em<?",
        params,
    ).fetchone()[0]
    ads = db.execute(
        "SELECT COUNT(*) FROM anuncios WHERE criado_em>=? AND criado_em<?", params
    ).fetchone()[0]
    orders = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE criado_em>=? AND criado_em<?", params
    ).fetchone()[0]
    affiliate_clicks = db.execute(
        "SELECT COUNT(*) FROM afiliado_eventos WHERE tipo_evento='click' "
        "AND ocorrido_em>=? AND ocorrido_em<?",
        params,
    ).fetchone()[0]
    suggestions = db.execute(
        "SELECT COUNT(*) FROM sugestoes_comunidade WHERE criado_em>=? AND criado_em<?",
        params,
    ).fetchone()[0]
    return {
        "empresas_visitadas": len(companies),
        "empresas_interessadas": sum(int(row["interested"]) for row in companies),
        "empresas_cadastradas": sum(int(row["registered"]) for row in companies),
        "bairros_visitados": len(
            {row["neighborhood"].strip().lower() for row in companies}
        ),
        "visitas_realizadas": sum(int(row["visits_count"]) for row in companies),
        "usuarios_conquistados": int(users),
        "novos_anuncios": int(ads),
        "pedidos": int(orders),
        "afiliados": int(affiliate_clicks),
        "sugestoes": int(suggestions),
    }


def _active_mission(db, weekly):
    row = db.execute(
        "SELECT * FROM growth_weekly_missions WHERE active=1 "
        "ORDER BY created_at DESC, id DESC LIMIT 1"
    ).fetchone()
    if not row:
        return None
    progress = int(weekly.get(row["metric"], 0))
    target = int(row["target"])
    return {
        "id": row["id"],
        "title": row["title"],
        "metric": row["metric"],
        "metric_label": MISSION_METRICS[row["metric"]],
        "target": target,
        "progress": progress,
        "percentage": min(100, round(progress * 100 / target)),
        "week_start": row["week_start"],
        "week_end": row["week_end"],
    }


def build_commercial_dashboard(db, now=None):
    period = _local_period(now)
    companies = list_companies(db)
    ambassadors = list_ambassadors(db)
    visited = len(companies)
    registered = sum(int(row["registered"]) for row in companies)
    metrics = {
        "visited": visited,
        "interested": sum(int(row["interested"]) for row in companies),
        "registered": registered,
        "partners": sum(int(row["partner"]) for row in companies),
        "neighborhoods": len(
            {row["neighborhood"].strip().lower() for row in companies}
        ),
        "visits": sum(int(row["visits_count"]) for row in companies),
        "conversion": round(registered * 100 / visited, 1) if visited else None,
        "conversion_label": (
            f"{registered * 100 / visited:.1f}%" if visited else "Aguardando base"
        ),
    }
    weekly = _weekly_counts(db, period)
    return {
        "generated_at": period["local_now"].strftime("%d/%m/%Y - %H:%M"),
        "week_label": (
            f"{period['start_date'].strftime('%d/%m')} a "
            f"{period['end_date'].strftime('%d/%m/%Y')}"
        ),
        "is_friday": period["local_now"].weekday() == 4,
        "metrics": metrics,
        "companies": companies,
        "ambassadors": ambassadors,
        "mission": _active_mission(db, weekly),
        "weekly": weekly,
        "mission_metrics": MISSION_METRICS,
    }


def _next_mission(data):
    weekly = data["weekly"]
    if weekly["empresas_visitadas"] == 0:
        return "Visitar o primeiro bairro e registrar cinco empresas."
    if weekly["empresas_cadastradas"] == 0:
        return "Converter a primeira empresa visitada em empresa cadastrada."
    if weekly["novos_anuncios"] == 0:
        return "Ajudar uma empresa cadastrada a publicar o primeiro anuncio."
    return "Aumentar empresas cadastradas sem reduzir a qualidade do acompanhamento."


def render_commercial_weekly_report(data):
    weekly = data["weekly"]
    mission = data["mission"]
    lines = [
        "# RELATORIO EXECUTIVO - CONQUISTAR COLATINA",
        "",
        f"**Semana:** {data['week_label']}",
        f"**Gerado em:** {data['generated_at']}",
        f"**Status:** {'Fechamento oficial de sexta-feira' if data['is_friday'] else 'Previa da semana'}",
        "",
        "## Resumo da semana",
        "",
        f"- Visitas realizadas: {weekly['visitas_realizadas']}",
        f"- Bairros visitados: {weekly['bairros_visitados']}",
        f"- Empresas visitadas: {weekly['empresas_visitadas']}",
        "",
        "## Empresas conquistadas",
        "",
        f"- Interessadas: {weekly['empresas_interessadas']}",
        f"- Cadastradas: {weekly['empresas_cadastradas']}",
        "",
        "## Indicadores da plataforma",
        "",
        f"- Usuarios conquistados: {weekly['usuarios_conquistados']}",
        f"- Anuncios novos: {weekly['novos_anuncios']}",
        f"- Pedidos: {weekly['pedidos']}",
        f"- Cliques de afiliados: {weekly['afiliados']}",
        f"- Sugestoes da comunidade: {weekly['sugestoes']}",
        "",
        "## Missao da semana",
        "",
        (
            f"{mission['title']} - {mission['progress']}/{mission['target']} "
            f"({mission['percentage']}%)."
            if mission
            else "Nenhuma missao principal foi definida."
        ),
        "",
        "## Missao seguinte",
        "",
        _next_mission(data),
        "",
    ]
    return "\n".join(lines)
