import re
from decimal import Decimal, InvalidOperation
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import requests


class MercadoLivreError(RuntimeError):
    pass


DOMINIOS_MERCADO_LIVRE = ("mercadolivre.com.br", "mercadolivre.com", "meli.la")


def _host_permitido(url):
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    host = (parsed.hostname or "").lower()
    return (
        parsed.scheme == "https"
        and not parsed.username
        and any(host == dominio or host.endswith(f".{dominio}") for dominio in DOMINIOS_MERCADO_LIVRE)
    )


def _resolver_link(link):
    atual = link
    headers = {"User-Agent": "MercadoColatina/1.0 (+https://mercado-colatina.onrender.com)"}
    for _ in range(6):
        if not _host_permitido(atual):
            raise MercadoLivreError("O link saiu dos domínios oficiais do Mercado Livre.")
        try:
            resposta = requests.get(
                atual,
                headers=headers,
                allow_redirects=False,
                stream=True,
                timeout=12,
            )
        except requests.RequestException as exc:
            raise MercadoLivreError("Não foi possível abrir a publicação do Mercado Livre.") from exc
        try:
            if resposta.is_redirect or resposta.is_permanent_redirect:
                destino = resposta.headers.get("Location", "")
                atual = urljoin(atual, destino)
                continue
        finally:
            resposta.close()
        break

    parsed = urlparse(atual)
    if "account-verification" in parsed.path:
        destino = parse_qs(parsed.query).get("go", [""])[0]
        if destino and _host_permitido(destino):
            atual = destino
    if not _host_permitido(atual):
        raise MercadoLivreError("A publicação não possui um endereço válido.")
    return atual


def _identificar_publicacao(url):
    parsed = urlparse(url)
    match = re.search(r"\bMLB-?(\d{6,})\b", f"{parsed.path}?{parsed.query}", re.I)
    if not match:
        raise MercadoLivreError("Não encontrei o código da publicação nesse link.")
    identificador = f"MLB{match.group(1)}"
    eh_catalogo = bool(re.search(r"/p/MLB-?\d+", parsed.path, re.I))
    return identificador, eh_catalogo


def _preco_brasileiro(valor):
    try:
        numero = Decimal(str(valor)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        return None
    inteiro, centavos = f"{numero:.2f}".split(".")
    inteiro = f"{int(inteiro):,}".replace(",", ".")
    return f"{inteiro},{centavos}"


def _titulo_do_link(url, identificador):
    partes = [unquote(parte) for parte in urlparse(url).path.split("/") if parte]
    candidatos = []
    for indice, parte in enumerate(partes):
        if identificador.lower() in parte.replace("-", "").lower():
            candidatos.append(parte)
            if re.fullmatch(r"MLB-?\d+", parte, re.I) and indice > 0:
                anterior = indice - 1
                if partes[anterior].lower() == "p" and anterior > 0:
                    anterior -= 1
                candidatos.insert(0, partes[anterior])
            break
    if not candidatos and partes:
        candidatos = [partes[0]]
    if not candidatos:
        return "Publicação do Mercado Livre"
    titulo = re.sub(r"^MLB-?\d+-?", "", candidatos[0], flags=re.I)
    titulo = re.sub(r"-?_JM$", "", titulo, flags=re.I)
    titulo = re.sub(r"[-_]+", " ", titulo).strip()
    return (titulo[:1].upper() + titulo[1:])[:120] if titulo else "Publicação do Mercado Livre"


def _dados_basicos(link, final, identificador):
    return {
        "titulo": _titulo_do_link(final, identificador),
        "descricao": "",
        "preco": "Consultar no Mercado Livre",
        "preco_anterior": None,
        "imagem_url": "",
        "link_afiliado": link,
    }


def _imagem_segura(dados):
    imagens = dados.get("pictures") or []
    if imagens:
        imagem = imagens[0].get("secure_url") or imagens[0].get("url") or ""
    else:
        imagem = dados.get("secure_thumbnail") or dados.get("thumbnail") or ""
    if imagem.startswith("http://"):
        imagem = "https://" + imagem[len("http://"):]
    return imagem if imagem.startswith("https://") else ""


def buscar_publicacao(link, access_token=None):
    final = _resolver_link(link)
    identificador, eh_catalogo = _identificar_publicacao(final)
    recurso = "products" if eh_catalogo else "items"
    headers = {"User-Agent": "MercadoColatina/1.0"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    try:
        resposta = requests.get(
            f"https://api.mercadolibre.com/{recurso}/{identificador}",
            headers=headers,
            timeout=15,
        )
        dados = resposta.json()
    except (requests.RequestException, ValueError):
        return _dados_basicos(link, final, identificador)
    if not resposta.ok:
        return _dados_basicos(link, final, identificador)

    titulo = (dados.get("name") if eh_catalogo else dados.get("title")) or ""
    if not titulo:
        raise MercadoLivreError("A publicação não retornou um título válido.")
    preco = _preco_brasileiro(dados.get("price")) or "Consultar no Mercado Livre"
    preco_anterior = _preco_brasileiro(dados.get("original_price"))
    descricao = ""
    resumo = dados.get("short_description")
    if isinstance(resumo, dict):
        descricao = str(resumo.get("content") or "").strip()[:240]

    return {
        "titulo": titulo.strip()[:120],
        "descricao": descricao,
        "preco": preco,
        "preco_anterior": preco_anterior,
        "imagem_url": _imagem_segura(dados),
        "link_afiliado": link,
    }
