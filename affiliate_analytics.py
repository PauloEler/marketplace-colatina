"""Registro e leitura das métricas anônimas de ofertas parceiras."""

from datetime import datetime, timedelta, timezone


COLATINA_TZ = timezone(timedelta(hours=-3))
VALID_EVENT_TYPES = frozenset({"click", "impression"})
VALID_DEVICES = frozenset({"desktop", "mobile"})
HOME_SOURCE = "home"


def _utc_timestamp(value):
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _offer_index(offers):
    return {offer["identificador_destino"]: offer for offer in offers}


def record_affiliate_event(db, offers, payload):
    """Valida no servidor e registra um evento sem dados pessoais."""

    event_type = str(payload.get("event_type", "")).strip().lower()
    offer_id = str(payload.get("offer_id", "")).strip().lower()
    device = str(payload.get("device", "")).strip().lower()
    offer = _offer_index(offers).get(offer_id)

    if event_type not in VALID_EVENT_TYPES or device not in VALID_DEVICES or not offer:
        return False

    db.execute(
        "INSERT INTO afiliado_eventos "
        "(parceiro, oferta_id, categoria, tipo_evento, origem, dispositivo) "
        "VALUES (?,?,?,?,?,?)",
        (
            offer["parceiro"],
            offer_id,
            offer["titulo"],
            event_type,
            HOME_SOURCE,
            device,
        ),
    )
    db.commit()
    return True


def build_affiliate_dashboard(db, offers, now=None):
    """Agrega cliques e impressões para o painel administrativo."""

    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)
    local_now = now.astimezone(COLATINA_TZ)
    local_day_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    cutoffs = {
        "today": _utc_timestamp(local_day_start),
        "7_days": _utc_timestamp(now - timedelta(days=7)),
        "30_days": _utc_timestamp(now - timedelta(days=30)),
    }

    click_totals = {}
    for key, cutoff in cutoffs.items():
        click_totals[key] = db.execute(
            "SELECT COUNT(*) FROM afiliado_eventos "
            "WHERE tipo_evento='click' AND ocorrido_em>=?",
            (cutoff,),
        ).fetchone()[0]

    rows = db.execute(
        "SELECT oferta_id, tipo_evento, COUNT(*) AS total "
        "FROM afiliado_eventos WHERE ocorrido_em>=? "
        "GROUP BY oferta_id, tipo_evento",
        (cutoffs["30_days"],),
    ).fetchall()
    totals = {}
    for row in rows:
        totals.setdefault(row["oferta_id"], {"click": 0, "impression": 0})
        totals[row["oferta_id"]][row["tipo_evento"]] = row["total"]

    categories = []
    for order, offer in enumerate(offers):
        values = totals.get(
            offer["identificador_destino"], {"click": 0, "impression": 0}
        )
        clicks = values["click"]
        impressions = values["impression"]
        ctr = round((clicks / impressions) * 100, 2) if impressions else 0.0
        categories.append(
            {
                "offer_id": offer["identificador_destino"],
                "category": offer["titulo"],
                "partner": offer["parceiro"],
                "clicks": clicks,
                "impressions": impressions,
                "ctr": ctr,
                "order": order,
            }
        )

    ranking = sorted(categories, key=lambda item: (-item["clicks"], item["order"]))
    top_category = ranking[0] if ranking and click_totals["30_days"] else None
    lowest_category = (
        sorted(categories, key=lambda item: (item["clicks"], item["order"]))[0]
        if categories and click_totals["30_days"]
        else None
    )

    return {
        "generated_at": local_now.strftime("%d/%m/%Y · %H:%M"),
        "clicks_today": click_totals["today"],
        "clicks_7_days": click_totals["7_days"],
        "clicks_30_days": click_totals["30_days"],
        "ranking": ranking,
        "top_category": top_category,
        "lowest_category": lowest_category,
    }
