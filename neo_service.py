import os
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel, Field


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.6-luna").strip()


class RascunhoAnuncio(BaseModel):
    titulo: str = Field(min_length=4, max_length=120)
    descricao: str = Field(min_length=10, max_length=1200)
    categoria: Literal[
        "Eletrônicos",
        "Móveis",
        "Roupas e Calçados",
        "Veículos",
        "Eletrodomésticos",
        "Imóveis",
        "Serviços",
        "Alimentos",
        "Outros",
    ]
    condicao: Literal["Novo", "Seminovo", "Usado"]
    requer_revisao: bool
    alerta: str = Field(max_length=240)


def configurado():
    return bool(OPENAI_API_KEY and OPENAI_MODEL)


def gerar_rascunho(relato):
    if not configurado():
        raise RuntimeError("Neo ainda não está configurado.")
    client = OpenAI(api_key=OPENAI_API_KEY, timeout=20.0, max_retries=1)
    resposta = client.responses.parse(
        model=OPENAI_MODEL,
        instructions=(
            "Você é o Neo, assistente do marketplace local Mercado Colatina. "
            "Transforme o relato do vendedor em um anúncio claro, honesto e objetivo em português do Brasil. "
            "Não invente marca, modelo, estado, garantia, acessórios ou características não informadas. "
            "Não inclua telefone, links, preço ou promessas. Se faltarem dados, indique na descrição o que o vendedor deve completar. "
            "Marque requer_revisao como verdadeiro para itens ilegais, perigosos, regulados, ofensivos, suspeitos ou quando o relato for insuficiente. "
            "Nesses casos, explique brevemente o motivo em alerta. Caso contrário, use alerta vazio."
        ),
        input=relato,
        text_format=RascunhoAnuncio,
    )
    if not resposta.output_parsed:
        raise RuntimeError("O Neo não conseguiu gerar um rascunho.")
    return resposta.output_parsed.model_dump()
