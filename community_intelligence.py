"""Agregações determinísticas para o Radar da Cidade, sem IA externa."""

import re
import unicodedata
from collections import Counter
from datetime import datetime, timedelta, timezone

from community_suggestions import SUGGESTION_CATEGORIES


PENDING_STATUSES = {"nova", "em_analise", "planejada"}
MINIMUM_CONCLUSIVE_SAMPLE = 3
INTELLIGENCE_SCHEMA_VERSION = "comunidade.v1"

_WORD_PATTERN = re.compile(r"[^\W\d_]+", re.UNICODE)
_STOP_WORDS = {
    "a",
    "ao",
    "aos",
    "aquela",
    "aquele",
    "aquilo",
    "as",
    "ate",
    "cada",
    "cidade",
    "colatina",
    "com",
    "como",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "ela",
    "ele",
    "em",
    "entre",
    "essa",
    "esse",
    "esta",
    "este",
    "eu",
    "falta",
    "faltando",
    "isso",
    "mais",
    "melhor",
    "melhoria",
    "mesma",
    "mesmo",
    "muito",
    "na",
    "nas",
    "no",
    "nos",
    "nossa",
    "nosso",
    "o",
    "os",
    "ou",
    "para",
    "pela",
    "pelas",
    "pelo",
    "pelos",
    "pessoa",
    "pessoas",
    "pode",
    "por",
    "porque",
    "precisa",
    "precisamos",
    "que",
    "sem",
    "ser",
    "seria",
    "sobre",
    "sua",
    "suas",
    "tem",
    "ter",
    "todo",
    "todos",
    "uma",
    "umas",
    "um",
    "uns",
}


def _sem_acento(valor):
    normalizado = unicodedata.normalize("NFKD", str(valor or "").lower())
    return "".join(letra for letra in normalizado if not unicodedata.combining(letra))


def _data_hora(valor):
    if not valor:
        return None
    if isinstance(valor, datetime):
        data = valor
    else:
        try:
            data = datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
        except ValueError:
            return None
    if data.tzinfo:
        data = data.astimezone(timezone.utc).replace(tzinfo=None)
    return data


def _formatar_tempo(minutos):
    if minutos is None:
        return "Sem dados"
    minutos = max(0, round(minutos))
    if minutos < 60:
        return f"{minutos} min"
    horas, resto = divmod(minutos, 60)
    if horas < 24:
        return f"{horas} h" + (f" {resto} min" if resto else "")
    dias, horas = divmod(horas, 24)
    return f"{dias} d" + (f" {horas} h" if horas else "")


def _palavras_relevantes(mensagem):
    palavras = []
    for original in _WORD_PATTERN.findall(str(mensagem or "").lower()):
        chave = _sem_acento(original)
        if len(chave) < 3 or chave in _STOP_WORDS:
            continue
        palavras.append((chave, original.capitalize()))
    return palavras


def construir_dataset_inteligencia(db, agora=None):
    """Entrega registros versionados e sem autoria para uma futura camada interna."""
    agora = _data_hora(agora) or datetime.now()
    linhas = db.execute(
        "SELECT id, categoria, mensagem, status, criado_em, analisada_em, "
        "implementada_em, atualizado_em FROM sugestoes_comunidade "
        "ORDER BY criado_em ASC, id ASC"
    ).fetchall()
    return {
        "schema_version": INTELLIGENCE_SCHEMA_VERSION,
        "fonte": "sugestoes_comunidade",
        "gerado_em": agora.isoformat(timespec="seconds"),
        "registros": [
            {
                "id": linha["id"],
                "categoria": linha["categoria"],
                "mensagem": linha["mensagem"],
                "status": linha["status"],
                "criado_em": linha["criado_em"],
                "analisada_em": linha["analisada_em"],
                "implementada_em": linha["implementada_em"],
                "atualizado_em": linha["atualizado_em"],
            }
            for linha in linhas
        ],
    }


def construir_inteligencia_comunidade(db, agora=None):
    agora = _data_hora(agora) or datetime.now()
    dataset = construir_dataset_inteligencia(db, agora)
    registros = dataset["registros"]
    total = len(registros)

    status = Counter(registro["status"] for registro in registros)
    categorias = Counter(registro["categoria"] for registro in registros)
    datas = {
        registro["id"]: _data_hora(registro["criado_em"]) for registro in registros
    }

    periodos = [
        {
            "chave": "hoje",
            "rotulo": "Hoje",
            "total": sum(
                1 for data in datas.values() if data and data.date() == agora.date()
            ),
        },
        {
            "chave": "7_dias",
            "rotulo": "Últimos 7 dias",
            "total": sum(
                1
                for data in datas.values()
                if data and data >= agora - timedelta(days=7)
            ),
        },
        {
            "chave": "30_dias",
            "rotulo": "Últimos 30 dias",
            "total": sum(
                1
                for data in datas.values()
                if data and data >= agora - timedelta(days=30)
            ),
        },
        {
            "chave": "90_dias",
            "rotulo": "Últimos 90 dias",
            "total": sum(
                1
                for data in datas.values()
                if data and data >= agora - timedelta(days=90)
            ),
        },
    ]

    ranking = [
        {
            "chave": chave,
            "categoria": SUGGESTION_CATEGORIES[chave],
            "total": categorias[chave],
            "percentual": round(categorias[chave] * 100 / total) if total else 0,
        }
        for chave in SUGGESTION_CATEGORIES
        if categorias[chave]
    ]
    ranking.sort(key=lambda item: (-item["total"], item["categoria"]))

    inicio_atual = agora - timedelta(days=30)
    inicio_anterior = agora - timedelta(days=60)
    atual = Counter()
    anterior = Counter()
    for registro in registros:
        data = datas[registro["id"]]
        if not data:
            continue
        if data >= inicio_atual:
            atual[registro["categoria"]] += 1
        elif data >= inicio_anterior:
            anterior[registro["categoria"]] += 1

    crescimento = [
        {
            "chave": chave,
            "categoria": SUGGESTION_CATEGORIES[chave],
            "atual": atual[chave],
            "anterior": anterior[chave],
            "variacao": atual[chave] - anterior[chave],
            "nova_ocorrencia": anterior[chave] == 0,
        }
        for chave in SUGGESTION_CATEGORIES
        if atual[chave] > anterior[chave]
    ]
    crescimento.sort(key=lambda item: (-item["variacao"], item["categoria"]))

    ocorrencias = Counter()
    sugestoes_por_palavra = Counter()
    rotulos = {}
    palavras_recentes = Counter()
    for registro in registros:
        tokens = _palavras_relevantes(registro["mensagem"])
        chaves_distintas = set()
        for chave, rotulo in tokens:
            rotulos.setdefault(chave, rotulo)
            ocorrencias[chave] += 1
            chaves_distintas.add(chave)
        for chave in chaves_distintas:
            sugestoes_por_palavra[chave] += 1
            data = datas[registro["id"]]
            if data and data >= inicio_atual:
                palavras_recentes[chave] += 1

    palavras = [
        {
            "chave": chave,
            "palavra": rotulos[chave],
            "sugestoes": sugestoes_por_palavra[chave],
            "ocorrencias": ocorrencias[chave],
        }
        for chave in sugestoes_por_palavra
    ]
    palavras.sort(
        key=lambda item: (-item["sugestoes"], -item["ocorrencias"], item["palavra"])
    )
    palavras = palavras[:12]
    recorrentes = [item for item in palavras if item["sugestoes"] >= 2][:8]

    tempos = []
    for registro in registros:
        criada = datas[registro["id"]]
        analisada = _data_hora(registro["analisada_em"])
        if criada and analisada:
            tempos.append(max(0, (analisada - criada).total_seconds() / 60))
    media = sum(tempos) / len(tempos) if tempos else None

    categoria_recente = None
    ranking_recente = sorted(
        (
            {
                "chave": chave,
                "categoria": SUGGESTION_CATEGORIES[chave],
                "total": quantidade,
            }
            for chave, quantidade in atual.items()
        ),
        key=lambda item: (-item["total"], item["categoria"]),
    )
    if ranking_recente:
        categoria_recente = ranking_recente[0]

    palavra_recente = None
    if palavras_recentes:
        chave, quantidade = sorted(
            palavras_recentes.items(), key=lambda item: (-item[1], rotulos[item[0]])
        )[0]
        palavra_recente = {
            "chave": chave,
            "palavra": rotulos[chave],
            "sugestoes": quantidade,
        }

    amostra_recente = periodos[2]["total"]
    if amostra_recente < MINIMUM_CONCLUSIVE_SAMPLE:
        resposta = {
            "conclusiva": False,
            "titulo": "Ainda não há dados suficientes",
            "descricao": (
                f"Os últimos 30 dias possuem {amostra_recente} "
                f"{'sugestão' if amostra_recente == 1 else 'sugestões'}. "
                "São necessárias pelo menos "
                f"{MINIMUM_CONCLUSIVE_SAMPLE} para apontar uma prioridade inicial."
            ),
        }
    else:
        lider = categoria_recente or ranking[0]
        complemento = (
            f" O termo mais recorrente no período é {palavra_recente['palavra']}."
            if palavra_recente
            else ""
        )
        resposta = {
            "conclusiva": True,
            "titulo": lider["categoria"],
            "descricao": (
                f"Esta é a categoria com mais registros nos últimos 30 dias "
                f"({lider['total']}).{complemento}"
            ),
        }

    return {
        "schema_version": dataset["schema_version"],
        "total": total,
        "implementadas": status["implementada"],
        "pendentes": sum(status[chave] for chave in PENDING_STATUSES),
        "arquivadas": status["arquivada"],
        "tempo_medio_analise": _formatar_tempo(media),
        "periodos": periodos,
        "ranking_categorias": ranking,
        "categorias_crescimento": crescimento,
        "palavras_frequentes": palavras,
        "sugestoes_recorrentes": recorrentes,
        "problemas_citados": palavras[:8],
        "categoria_recente": categoria_recente,
        "palavra_recente": palavra_recente,
        "resposta_cidade": resposta,
    }
