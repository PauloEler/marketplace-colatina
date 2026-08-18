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
    "balance_status": "Saldo pré-pago conferido",
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


def build_campaign_dashboard():
    """Monta indicadores sem transformar ausência de medição em resultado."""

    campaigns = deepcopy(CAMPAIGN_SNAPSHOTS)
    impressions = sum(item["metrics"]["impressions"] for item in campaigns)
    clicks = sum(item["metrics"]["clicks"] for item in campaigns)
    cost = round(sum(item["metrics"]["cost"] for item in campaigns), 2)

    for campaign in campaigns:
        metrics = campaign["metrics"]
        metrics["ctr"] = _calculate_ctr(metrics["clicks"], metrics["impressions"])

    return {
        "generated_at": "18/08/2026",
        "data_mode": "Atualização manual",
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
        "measurement_note": (
            "Os números refletem a última conferência manual. "
            "Não há integração automática com as plataformas nesta versão."
        ),
    }
