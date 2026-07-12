import base64
import hashlib
import os
from urllib.parse import urlencode

import mercadopago
import requests
from cryptography.fernet import Fernet, InvalidToken
from mercadopago.webhook import InvalidWebhookSignatureError, WebhookSignatureValidator


CLIENT_ID = os.environ.get("MP_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("MP_CLIENT_SECRET", "")
WEBHOOK_SECRET = os.environ.get("MP_WEBHOOK_SECRET", "")
REDIRECT_URI = os.environ.get(
    "MP_REDIRECT_URI",
    "https://mercado-colatina.onrender.com/mercadopago/oauth/callback",
)
AUTH_URL = "https://auth.mercadopago.com/authorization"
OAUTH_TOKEN_URL = "https://api.mercadopago.com/oauth/token"


class MercadoPagoError(RuntimeError):
    pass


def configurado():
    return bool(CLIENT_ID and CLIENT_SECRET and REDIRECT_URI)


def pagamentos_configurados():
    """Só libera cobranças quando OAuth e confirmação por webhook estão prontos."""
    return configurado() and bool(WEBHOOK_SECRET)


def _fernet(secret_key):
    digest = hashlib.sha256(secret_key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def criptografar_token(valor, secret_key):
    if not valor:
        return None
    return _fernet(secret_key).encrypt(valor.encode("utf-8")).decode("ascii")


def descriptografar_token(valor, secret_key):
    if not valor:
        return None
    try:
        return _fernet(secret_key).decrypt(valor.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError, TypeError) as exc:
        raise MercadoPagoError("Credencial do vendedor indisponivel.") from exc


def criar_url_autorizacao(state, code_challenge):
    if not configurado():
        raise MercadoPagoError("Mercado Pago ainda nao esta configurado.")
    parametros = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "platform_id": "mp",
        "state": state,
        "redirect_uri": REDIRECT_URI,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return f"{AUTH_URL}?{urlencode(parametros)}"


def trocar_codigo_por_token(code, code_verifier):
    resposta = requests.post(
        OAUTH_TOKEN_URL,
        json={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "code_verifier": code_verifier,
            "test_token": False,
        },
        timeout=15,
    )
    return _validar_resposta_http(resposta)


def renovar_token(refresh_token):
    resposta = requests.post(
        OAUTH_TOKEN_URL,
        json={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        timeout=15,
    )
    return _validar_resposta_http(resposta)


def _validar_resposta_http(resposta):
    try:
        dados = resposta.json()
    except ValueError as exc:
        raise MercadoPagoError("Resposta invalida do Mercado Pago.") from exc
    if not resposta.ok:
        mensagem = (
            dados.get("message") or dados.get("error") or "Falha no Mercado Pago."
        )
        raise MercadoPagoError(str(mensagem))
    return dados


def _validar_resposta_sdk(resultado):
    status = int(resultado.get("status", 500))
    dados = resultado.get("response") or {}
    if status < 200 or status >= 300:
        mensagem = (
            dados.get("message") or dados.get("error") or "Falha no Mercado Pago."
        )
        raise MercadoPagoError(str(mensagem))
    return dados


def criar_preferencia(access_token, dados):
    sdk = mercadopago.SDK(access_token)
    return _validar_resposta_sdk(sdk.preference().create(dados))


def consultar_pagamento(access_token, payment_id):
    sdk = mercadopago.SDK(access_token)
    return _validar_resposta_sdk(sdk.payment().get(str(payment_id)))


def webhook_valido(x_signature, x_request_id, data_id):
    if not WEBHOOK_SECRET:
        return False
    try:
        WebhookSignatureValidator.validate(
            x_signature,
            x_request_id,
            str(data_id),
            WEBHOOK_SECRET,
        )
        return True
    except (InvalidWebhookSignatureError, ValueError, TypeError):
        return False
