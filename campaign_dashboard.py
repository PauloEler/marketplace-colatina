"""Retrato operacional das campanhas de divulgação do Mercado Colatina.

Os dados deste módulo são conferências manuais. A estrutura separa a origem dos
dados da apresentação para permitir integrações oficiais no futuro sem acoplar
o dashboard ao Google Ads ou à Meta.
"""

from copy import deepcopy


CAMPAIGN_ACCOUNT = {
    "provider": "Google Ads",
    "account_id": "333-169-5325",
    "available_balance": 250.0,
    "balance_status": "Saldo conferido manualmente em 18/08/2026",
    "automatic_recharge": False,
}

CAMPAIGN_SNAPSHOTS = (
    {
        "key": "mercado-colatina-001",
        "name": "Pesquisa — Mercado Colatina — Campanha 001",
        "brand": "Mercado Colatina",
        "channel": "Pesquisa Google",
        "objective": "Levar moradores de Colatina ao marketplace local",
        "status": "Ativa",
        "approval": "Qualificada",
        "quality": "Médio",
        "location": "Colatina",
        "location_mode": "Presença na região",
        "daily_budget": None,
        "started_at": None,
        "metrics": {
            "impressions": 0,
            "clicks": 0,
            "cost": 0.0,
            "conversions": None,
        },
        "keywords": (),
        "keyword_status": None,
        "next_action": "Aguardar volume e revisar termos de pesquisa.",
        "updated_at": "18/08/2026",
        "source": "Conferência manual no Google Ads",
    },
    {
        "key": "topa-tudo-colatinense-001",
        "campaign_id": "24087985650",
        "name": "Pesquisa — Topa Tudo Colatinense — Campanha 001",
        "brand": "Topa Tudo Colatinense",
        "channel": "Pesquisa Google",
        "objective": "Atrair buscas locais por celulares e produtos usados",
        "status": "Ativa",
        "approval": "Qualificada",
        "quality": "Médio",
        "location": "Colatina",
        "location_mode": "Presença na região",
        "daily_budget": 10.0,
        "started_at": "01/08/2026",
        "metrics": {
            "impressions": 0,
            "clicks": 0,
            "cost": 0.0,
            "conversions": None,
        },
        "keywords": (
            "celular barato",
            "comprar celular",
            "celular motorola",
            "móveis usados",
            "eletrodomésticos usados",
            "loja de usados",
        ),
        "keyword_status": "Em revisão após inclusão",
        "next_action": "Confirmar aprovação das palavras e observar as primeiras 48 h.",
        "updated_at": "18/08/2026",
        "source": "Conferência manual no Google Ads",
    },
)


def _calculate_ctr(clicks, impressions):
    if not impressions:
        return None
    return round((clicks / impressions) * 100, 2)


def _normalized_name(value):
    return " ".join(str(value or "").strip().lower().split())


def _live_campaign_index(live_campaigns):
    by_id = {}
    by_name = {}
    for campaign in live_campaigns:
        campaign_id = str(campaign.get("campaign_id", ""))
        if campaign_id:
            by_id[campaign_id] = campaign
        by_name[_normalized_name(campaign.get("name"))] = campaign
    return by_id, by_name


def _merge_live_campaigns(campaigns, integration):
    if not integration.get("connected"):
        return campaigns
    by_id, by_name = _live_campaign_index(integration.get("campaigns", ()))
    for campaign in campaigns:
        live = by_id.get(str(campaign.get("campaign_id", "")))
        if not live:
            live = by_name.get(_normalized_name(campaign["name"]))
        if not live:
            campaign["sync_warning"] = "Campanha não localizada na resposta da API."
            continue
        campaign["campaign_id"] = live.get("campaign_id") or campaign.get("campaign_id")
        campaign["status"] = {
            "ENABLED": "Ativa",
            "PAUSED": "Pausada",
            "REMOVED": "Removida",
        }.get(live.get("status"), "Estado não identificado")
        campaign["daily_budget"] = live.get("daily_budget")
        campaign["started_at"] = live.get("started_at") or campaign.get("started_at")
        campaign["metrics"] = deepcopy(live["metrics"])
        campaign["source"] = "Google Ads API"
        campaign["updated_at"] = integration["synced_at"]
    return campaigns


def build_campaign_dashboard(integration=None):
    """Monta indicadores sem transformar ausência de medição em resultado."""

    integration = integration or {
        "connected": False,
        "mode": "Dados manuais de segurança",
        "message": "Integração automática não consultada.",
        "synced_at": None,
        "period": "Última conferência manual",
        "campaigns": (),
        "missing": (),
    }
    campaigns = _merge_live_campaigns(deepcopy(CAMPAIGN_SNAPSHOTS), integration)
    impressions = sum(item["metrics"]["impressions"] for item in campaigns)
    clicks = sum(item["metrics"]["clicks"] for item in campaigns)
    cost = round(sum(item["metrics"]["cost"] for item in campaigns), 2)

    for campaign in campaigns:
        metrics = campaign["metrics"]
        metrics["ctr"] = _calculate_ctr(metrics["clicks"], metrics["impressions"])

    return {
        "generated_at": integration.get("synced_at") or "18/08/2026",
        "data_mode": integration["mode"],
        "integration": integration,
        "period": integration["period"],
        "account": deepcopy(CAMPAIGN_ACCOUNT),
        "summary": {
            "tracked": len(campaigns),
            "active": sum(item["status"] == "Ativa" for item in campaigns),
            "impressions": impressions,
            "clicks": clicks,
            "cost": cost,
            "ctr": _calculate_ctr(clicks, impressions),
        },
        "campaigns": campaigns,
        "future_channels": ("Facebook", "Instagram", "WhatsApp Status"),
        "measurement_note": integration["message"],
    }
