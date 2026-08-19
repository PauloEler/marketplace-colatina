"""Integração somente leitura com a API oficial do Google Ads."""

import os
import re
import threading
import time
from datetime import datetime, timedelta, timezone

import requests


COLATINA_TZ = timezone(timedelta(hours=-3))
TOKEN_URL = "https://oauth2.googleapis.com/token"
DEFAULT_API_VERSION = "v25"
DEFAULT_CACHE_TTL = 900
REQUEST_TIMEOUT = 12
REQUIRED_CREDENTIALS = (
    "GOOGLE_ADS_DEVELOPER_TOKEN",
    "GOOGLE_ADS_CLIENT_ID",
    "GOOGLE_ADS_CLIENT_SECRET",
    "GOOGLE_ADS_REFRESH_TOKEN",
)

_cache_lock = threading.Lock()
_cache = {"expires_at": 0.0, "value": None}


class GoogleAdsIntegrationError(RuntimeError):
    """Erro seguro para exibição no painel administrativo."""


def _digits(value):
    return re.sub(r"\D", "", str(value or ""))


def _configuration():
    customer_id = _digits(os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "3331695325"))
    api_version = os.environ.get("GOOGLE_ADS_API_VERSION", DEFAULT_API_VERSION)
    if not re.fullmatch(r"v\d+", api_version):
        api_version = DEFAULT_API_VERSION

    missing = [name for name in REQUIRED_CREDENTIALS if not os.environ.get(name)]
    if not customer_id:
        missing.append("GOOGLE_ADS_CUSTOMER_ID")

    try:
        cache_ttl = max(
            60,
            int(os.environ.get("GOOGLE_ADS_SYNC_TTL_SECONDS", DEFAULT_CACHE_TTL)),
        )
    except ValueError:
        cache_ttl = DEFAULT_CACHE_TTL

    return {
        "customer_id": customer_id,
        "login_customer_id": _digits(
            os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")
        ),
        "developer_token": os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", ""),
        "client_id": os.environ.get("GOOGLE_ADS_CLIENT_ID", ""),
        "client_secret": os.environ.get("GOOGLE_ADS_CLIENT_SECRET", ""),
        "refresh_token": os.environ.get("GOOGLE_ADS_REFRESH_TOKEN", ""),
        "api_version": api_version,
        "cache_ttl": cache_ttl,
        "missing": missing,
    }


def _access_token(config):
    try:
        response = requests.post(
            TOKEN_URL,
            data={
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "refresh_token": config["refresh_token"],
                "grant_type": "refresh_token",
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        token = response.json().get("access_token")
    except (requests.RequestException, ValueError) as error:
        raise GoogleAdsIntegrationError(
            "Não foi possível autenticar a integração com o Google Ads."
        ) from error
    if not token:
        raise GoogleAdsIntegrationError(
            "O Google não devolveu uma credencial de acesso válida."
        )
    return token


def _query_campaigns(config, access_token):
    query = """
        SELECT
          campaign.id,
          campaign.name,
          campaign.status,
          campaign_budget.amount_micros,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions
        FROM campaign
        WHERE campaign.status != 'REMOVED'
          AND segments.date DURING LAST_30_DAYS
        ORDER BY campaign.name
    """
    url = (
        "https://googleads.googleapis.com/"
        f"{config['api_version']}/customers/{config['customer_id']}/googleAds:search"
    )
    headers = {
        "Authorization": f"Bearer {access_token}",
        "developer-token": config["developer_token"],
        "Content-Type": "application/json",
    }
    if config["login_customer_id"]:
        headers["login-customer-id"] = config["login_customer_id"]

    results = []
    page_token = None
    while True:
        payload = {"query": query}
        if page_token:
            payload["pageToken"] = page_token
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as error:
            raise GoogleAdsIntegrationError(
                "A API do Google Ads não respondeu à consulta de campanhas."
            ) from error
        results.extend(data.get("results", ()))
        page_token = data.get("nextPageToken")
        if not page_token:
            return results


def _number(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_result(row):
    campaign = row.get("campaign", {})
    budget = row.get("campaignBudget", {})
    metrics = row.get("metrics", {})
    return {
        "campaign_id": str(campaign.get("id", "")),
        "name": campaign.get("name", "Campanha sem nome"),
        "status": campaign.get("status", "UNKNOWN"),
        "started_at": campaign.get("startDate") or None,
        "ended_at": campaign.get("endDate") or None,
        "daily_budget": round(_number(budget.get("amountMicros")) / 1_000_000, 2),
        "metrics": {
            "impressions": int(_number(metrics.get("impressions"))),
            "clicks": int(_number(metrics.get("clicks"))),
            "cost": round(_number(metrics.get("costMicros")) / 1_000_000, 2),
            "conversions": round(_number(metrics.get("conversions")), 2),
        },
    }


def _live_snapshot(config, now=None):
    now = now or datetime.now(timezone.utc)
    token = _access_token(config)
    campaigns = [_normalize_result(row) for row in _query_campaigns(config, token)]
    return {
        "connected": True,
        "mode": "Integração automática",
        "message": "Métricas sincronizadas pela API oficial do Google Ads.",
        "synced_at": now.astimezone(COLATINA_TZ).strftime("%d/%m/%Y · %H:%M"),
        "period": "Últimos 30 dias",
        "campaigns": campaigns,
    }


def get_google_ads_snapshot(force=False, now=None):
    """Busca o retrato atual e usa cache para proteger a cota da API."""

    config = _configuration()
    if config["missing"]:
        return {
            "connected": False,
            "mode": "Dados manuais de segurança",
            "message": "Credenciais oficiais do Google Ads ainda não configuradas.",
            "synced_at": None,
            "period": "Última conferência manual",
            "campaigns": (),
            "missing": tuple(config["missing"]),
        }

    with _cache_lock:
        if not force and _cache["value"] and _cache["expires_at"] > time.monotonic():
            return _cache["value"]
        try:
            value = _live_snapshot(config, now=now)
        except GoogleAdsIntegrationError as error:
            return {
                "connected": False,
                "mode": "Dados manuais de segurança",
                "message": str(error),
                "synced_at": None,
                "period": "Última conferência manual",
                "campaigns": (),
                "missing": (),
            }
        _cache["value"] = value
        _cache["expires_at"] = time.monotonic() + config["cache_ttl"]
        return value


def reset_google_ads_cache():
    """Limpa o cache; usado por testes e por uma atualização administrativa."""

    with _cache_lock:
        _cache["expires_at"] = 0.0
        _cache["value"] = None
