"""Configuracao centralizada das ofertas de parceiros da Home."""

import os
from collections.abc import Mapping


PARTNER_OFFERS_CONFIG = (
    {
        "parceiro": "mercado_livre",
        "titulo": "Tripé para celular Ulanzi MA09",
        "preco": "Veja preço e condições no site parceiro",
        "imagem": "oferta-parceiro-07-ulanzi-ma09-premium.webp",
        "alt": (
            "Imagem ilustrativa de tripé para celular com controle remoto "
            "em oferta parceira"
        ),
        "identificador_destino": "tripe-ulanzi-ma09",
        "env_key": "OFERTA_PARCEIRO_07_URL",
        "official_url": "https://meli.la/2gSYwQb",
        "fallback_url": (
            "https://www.mercadolivre.com.br/"
            "tripe-basto-para-celular-ulanzi-ma09-com-controle-remoto/"
            "p/MLB36175790"
        ),
    },
    {
        "parceiro": "mercado_livre",
        "titulo": "Fone JBL Tune 520BT",
        "preco": "Veja preço e condições no site parceiro",
        "imagem": "oferta-parceiro-08-jbl-tune-520bt-premium.webp",
        "alt": "Imagem ilustrativa de fone sem fio azul em oferta parceira",
        "identificador_destino": "fone-jbl-tune-520bt",
        "env_key": "OFERTA_PARCEIRO_08_URL",
        "official_url": "https://meli.la/2uTaby6",
        "fallback_url": (
            "https://www.mercadolivre.com.br/"
            "fone-de-ouvido-jbl-tune-520bt-bluetooth-53-preto-cor-azul/"
            "p/MLB52695692"
        ),
    },
    {
        "parceiro": "mercado_livre",
        "titulo": "Air Fryer Oven WAP WAOD2",
        "preco": "Veja preço e condições no site parceiro",
        "imagem": "oferta-parceiro-09-airfryer-wap-premium.webp",
        "alt": "Imagem ilustrativa de air fryer oven preta em oferta parceira",
        "identificador_destino": "airfryer-wap-waod2",
        "env_key": "OFERTA_PARCEIRO_09_URL",
        "official_url": "https://meli.la/1K1uUf6",
        "fallback_url": (
            "https://www.mercadolivre.com.br/"
            "fritadeira-eletrica-air-fryer-oven-black-inox-wap-waod2/"
            "p/MLB43435820"
        ),
    },
    {
        "parceiro": "mercado_livre",
        "titulo": "Parafusadeira WAP 12K3.2 com maleta",
        "preco": "Veja preço e condições no site parceiro",
        "imagem": "oferta-parceiro-10-parafusadeira-wap-premium.webp",
        "alt": "Imagem ilustrativa de parafusadeira sem fio com maleta",
        "identificador_destino": "parafusadeira-wap-12k32",
        "env_key": "OFERTA_PARCEIRO_10_URL",
        "official_url": "https://meli.la/2oKG2qM",
        "fallback_url": (
            "https://www.mercadolivre.com.br/"
            "parafusadeira-e-furadeira-a-bateria-wap-bpf-12k32-com-maleta/"
            "p/MLB47815092"
        ),
    },
    {
        "parceiro": "mercado_livre",
        "titulo": "Kit 10 Potes Herméticos de Vidro",
        "preco": "Veja preço e condições no site parceiro",
        "imagem": "oferta-parceiro-11-potes-vidro-premium.webp",
        "alt": "Imagem ilustrativa de potes herméticos de vidro para alimentos",
        "identificador_destino": "kit-potes-vidro-hermeticos",
        "env_key": "OFERTA_PARCEIRO_11_URL",
        "official_url": "https://meli.la/1VhuyQ1",
        "fallback_url": (
            "https://www.mercadolivre.com.br/"
            "kit-10-potes-hermeticos-vidro-640ml-starhouse-marmita-forno-"
            "micro-ondas-airfryer-com-4-travas-de-super-vedacao/"
            "p/MLB53222689"
        ),
    },
    {
        "parceiro": "mercado_livre",
        "titulo": "Celulares e acessórios",
        "preco": "A partir de R$ 49,90",
        "imagem": "oferta-parceiro-01-premium.webp",
        "alt": "Celular e acessórios em composição fotográfica de oferta parceira",
        "identificador_destino": "celulares-acessorios",
        "env_key": "OFERTA_PARCEIRO_01_URL",
        "official_url": "https://meli.la/2Etz5JQ",
        "fallback_url": "https://lista.mercadolivre.com.br/celulares-acessorios",
    },
    {
        "parceiro": "mercado_livre",
        "titulo": "Fones e áudio",
        "preco": "A partir de R$ 39,90",
        "imagem": "oferta-parceiro-02-premium.webp",
        "alt": "Fones e produtos de áudio em composição fotográfica de oferta parceira",
        "identificador_destino": "fones-audio",
        "env_key": "OFERTA_PARCEIRO_02_URL",
        "official_url": "https://meli.la/2wXKKkG",
        "fallback_url": "https://lista.mercadolivre.com.br/fones-audio",
    },
    {
        "parceiro": "mercado_livre",
        "titulo": "Informática",
        "preco": "A partir de R$ 89,90",
        "imagem": "oferta-parceiro-03-premium.webp",
        "alt": "Notebook e itens de informática em composição fotográfica de oferta parceira",
        "identificador_destino": "informatica",
        "env_key": "OFERTA_PARCEIRO_03_URL",
        "official_url": "https://meli.la/2w5Db1g",
        "fallback_url": "https://lista.mercadolivre.com.br/informatica",
    },
    {
        "parceiro": "mercado_livre",
        "titulo": "Casa e utilidades",
        "preco": "A partir de R$ 29,90",
        "imagem": "oferta-parceiro-04-premium.webp",
        "alt": "Itens para casa em composição fotográfica de oferta parceira",
        "identificador_destino": "casa-utilidades",
        "env_key": "OFERTA_PARCEIRO_04_URL",
        "official_url": "https://meli.la/2UFigfL",
        "fallback_url": "https://lista.mercadolivre.com.br/casa-utilidades",
    },
    {
        "parceiro": "mercado_livre",
        "titulo": "Ferramentas",
        "preco": "A partir de R$ 59,90",
        "imagem": "oferta-parceiro-05-premium.webp",
        "alt": "Ferramentas em composição fotográfica de oferta parceira",
        "identificador_destino": "ferramentas",
        "env_key": "OFERTA_PARCEIRO_05_URL",
        "official_url": "https://meli.la/1Cfu3iY",
        "fallback_url": "https://lista.mercadolivre.com.br/ferramentas",
    },
    {
        "parceiro": "mercado_livre",
        "titulo": "Eletroportáteis",
        "preco": "A partir de R$ 79,90",
        "imagem": "oferta-parceiro-06-premium.webp",
        "alt": "Eletroportáteis em composição fotográfica de oferta parceira",
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
