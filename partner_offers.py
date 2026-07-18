"""Configuracao centralizada das ofertas de parceiros da Home."""

import os
from collections.abc import Mapping


PARTNER_OFFERS_CONFIG = (
    {
        "titulo": "Celulares e acessórios",
        "preco": "A partir de R$ 49,90",
        "imagem": "oferta-parceiro-01.svg",
        "alt": "Ilustração de celular e acessórios em oferta parceira",
        "identificador_destino": "celulares-acessorios",
        "env_key": "OFERTA_PARCEIRO_01_URL",
        "official_url": "https://meli.la/2Etz5JQ",
        "fallback_url": "https://lista.mercadolivre.com.br/celulares-acessorios",
    },
    {
        "titulo": "Fones e áudio",
        "preco": "A partir de R$ 39,90",
        "imagem": "oferta-parceiro-02.svg",
        "alt": "Ilustração de fones e produtos de áudio em oferta parceira",
        "identificador_destino": "fones-audio",
        "env_key": "OFERTA_PARCEIRO_02_URL",
        "official_url": "https://meli.la/2wXKKkG",
        "fallback_url": "https://lista.mercadolivre.com.br/fones-audio",
    },
    {
        "titulo": "Informática",
        "preco": "A partir de R$ 89,90",
        "imagem": "oferta-parceiro-03.svg",
        "alt": "Ilustração de notebook e itens de informática em oferta parceira",
        "identificador_destino": "informatica",
        "env_key": "OFERTA_PARCEIRO_03_URL",
        "official_url": "https://meli.la/2w5Db1g",
        "fallback_url": "https://lista.mercadolivre.com.br/informatica",
    },
    {
        "titulo": "Casa e utilidades",
        "preco": "A partir de R$ 29,90",
        "imagem": "oferta-parceiro-04.svg",
        "alt": "Ilustração de itens para casa em oferta parceira",
        "identificador_destino": "casa-utilidades",
        "env_key": "OFERTA_PARCEIRO_04_URL",
        "official_url": "https://meli.la/2UFigfL",
        "fallback_url": "https://lista.mercadolivre.com.br/casa-utilidades",
    },
    {
        "titulo": "Ferramentas",
        "preco": "A partir de R$ 59,90",
        "imagem": "oferta-parceiro-05.svg",
        "alt": "Ilustração de ferramentas em oferta parceira",
        "identificador_destino": "ferramentas",
        "env_key": "OFERTA_PARCEIRO_05_URL",
        "official_url": "https://meli.la/1Cfu3iY",
        "fallback_url": "https://lista.mercadolivre.com.br/ferramentas",
    },
    {
        "titulo": "Eletroportáteis",
        "preco": "A partir de R$ 79,90",
        "imagem": "oferta-parceiro-06.svg",
        "alt": "Ilustração de eletroportáteis em oferta parceira",
        "identificador_destino": "eletroportateis",
        "env_key": "OFERTA_PARCEIRO_06_URL",
        "official_url": "https://meli.la/2BrRKKT",
        "fallback_url": "https://lista.mercadolivre.com.br/eletroportateis",
    },
)


def build_partner_offers(environ: Mapping[str, str] | None = None) -> tuple[dict, ...]:
    """Monta as ofertas usando o link oficial quando ele estiver configurado."""

    source = os.environ if environ is None else environ
    offers = []

    for config in PARTNER_OFFERS_CONFIG:
        configured_url = source.get(config["env_key"], "").strip()
        official_url = configured_url or config["official_url"]
        offer = {
            key: value
            for key, value in config.items()
            if key not in {"env_key", "official_url", "fallback_url"}
        }
        offer.update(
            {
                "url": official_url or config["fallback_url"],
                "env_key": config["env_key"],
                "link_oficial_configurado": bool(official_url),
            }
        )
        offers.append(offer)

    return tuple(offers)
