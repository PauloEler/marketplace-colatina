import os
import re
import secrets
import base64
import hashlib
import hmac
import json
import time
import unicodedata
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import quote

from flask import (
    Flask,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

from database import USE_PG, close_db, get_db, init_db  # noqa: E402
from mercadopago_service import (  # noqa: E402
    MercadoPagoError,
    configurado as mercadopago_configurado,
    pagamentos_configurados as mercadopago_pagamentos_configurados,
    consultar_pagamento,
    criar_preferencia,
    criar_url_autorizacao,
    criptografar_token,
    descriptografar_token,
    renovar_token,
    trocar_codigo_por_token,
    webhook_valido,
)
from storage import excluir_imagem, salvar_imagem  # noqa: E402
from neo_service import configurado as neo_configurado, gerar_rascunho  # noqa: E402
from email_service import (  # noqa: E402
    destinatario_admin,
    email_configurado,
    enviar_alerta_novo_pedido,
    enviar_teste_admin,
)

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY")
FLASK_ENV = os.environ.get("FLASK_ENV", "production")

if not SECRET_KEY:
    if FLASK_ENV == "production":
        raise RuntimeError("SECRET_KEY precisa estar definida em producao.")
    SECRET_KEY = secrets.token_hex(32)

app.secret_key = SECRET_KEY
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = FLASK_ENV == "production"
app.config["MAX_FORM_MEMORY_SIZE"] = 6 * 1024 * 1024

BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(BASE_DIR, "uploads"))
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

CATEGORIA_ALIASES = {
    "Eletrônicos": ("Eletrônicos", "Eletronicos"),
    "Móveis": ("Móveis", "Moveis"),
    "Roupas e Calçados": ("Roupas e Calçados", "Roupas e Calcados"),
    "Veículos": ("Veículos", "Veiculos"),
    "Eletrodomésticos": ("Eletrodomésticos", "Eletrodomesticos"),
    "Imóveis": ("Imóveis", "Imoveis"),
    "Serviços": ("Serviços", "Servicos"),
    "Alimentos": ("Alimentos",),
    "Outros": ("Outros",),
}
CATEGORIAS = list(CATEGORIA_ALIASES)
CATEGORIA_CANONICA = {
    alias: categoria
    for categoria, aliases in CATEGORIA_ALIASES.items()
    for alias in aliases
}

LIMITE_GRATIS = 10
try:
    LIMITE_FUNDADORES = int(os.environ.get("FOUNDERS_LIMIT", "100"))
except ValueError:
    LIMITE_FUNDADORES = 100
LIMITE_FUNDADORES = max(0, min(LIMITE_FUNDADORES, 10000))
try:
    LOJA_OFICIAL_ID = int(os.environ.get("OFFICIAL_STORE_ID", "1"))
except ValueError:
    LOJA_OFICIAL_ID = 1
VALOR_PLANO = os.environ.get("PLAN_PRICE_DISPLAY", "R$ 10,00")
VALOR_PLANO_BANCO = os.environ.get("PLAN_PRICE", "10.00")
PIX_CHAVE = os.environ.get("PIX_KEY", "27998984840")
PIX_TITULAR = os.environ.get("PIX_RECEIVER_NAME", "Mercado Colatina")
PAGAMENTO_WHATSAPP = os.environ.get(
    "PAYMENT_WHATSAPP", os.environ.get("ADMIN_WHATSAPP", PIX_CHAVE)
)
SUPPORT_WHATSAPP = os.environ.get(
    "SUPPORT_WHATSAPP", os.environ.get("ADMIN_WHATSAPP", PIX_CHAVE)
)
MERCADO_LIVRE_AFILIADO_URL = os.environ.get(
    "MERCADO_LIVRE_AFILIADO_URL", "https://meli.la/1yyfAoN"
)
OFERTAS_PARCEIROS_HOME = (
    {
        "titulo": "Celulares e acessórios",
        "preco": "A partir de R$ 49,90",
        "imagem": "oferta-parceiro-01.svg",
        "alt": "Ilustração de celular e acessórios em oferta parceira",
        "url": MERCADO_LIVRE_AFILIADO_URL,
    },
    {
        "titulo": "Fones e áudio",
        "preco": "A partir de R$ 39,90",
        "imagem": "oferta-parceiro-02.svg",
        "alt": "Ilustração de fones e produtos de áudio em oferta parceira",
        "url": MERCADO_LIVRE_AFILIADO_URL,
    },
    {
        "titulo": "Informática",
        "preco": "A partir de R$ 89,90",
        "imagem": "oferta-parceiro-03.svg",
        "alt": "Ilustração de notebook e itens de informática em oferta parceira",
        "url": MERCADO_LIVRE_AFILIADO_URL,
    },
    {
        "titulo": "Casa e utilidades",
        "preco": "A partir de R$ 29,90",
        "imagem": "oferta-parceiro-04.svg",
        "alt": "Ilustração de itens para casa em oferta parceira",
        "url": MERCADO_LIVRE_AFILIADO_URL,
    },
    {
        "titulo": "Ferramentas",
        "preco": "A partir de R$ 59,90",
        "imagem": "oferta-parceiro-05.svg",
        "alt": "Ilustração de ferramentas em oferta parceira",
        "url": MERCADO_LIVRE_AFILIADO_URL,
    },
    {
        "titulo": "Eletroportáteis",
        "preco": "A partir de R$ 79,90",
        "imagem": "oferta-parceiro-06.svg",
        "alt": "Ilustração de eletroportáteis em oferta parceira",
        "url": MERCADO_LIVRE_AFILIADO_URL,
    },
)
try:
    MARKETPLACE_FEE_PERCENT = Decimal(os.environ.get("MARKETPLACE_FEE_PERCENT", "0"))
except InvalidOperation:
    MARKETPLACE_FEE_PERCENT = Decimal("0")
if MARKETPLACE_FEE_PERCENT < 0 or MARKETPLACE_FEE_PERCENT > 30:
    MARKETPLACE_FEE_PERCENT = Decimal("0")
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,24}$")
PEDIDO_STATUS = {
    "aguardando": "Aguardando vendedor",
    "confirmado": "Pedido confirmado",
    "em_analise": "Em analise",
    "concluido": "Compra concluída",
    "cancelado": "Pedido cancelado",
    "recusado": "Pedido recusado",
}
PEDIDO_ENTREGA = {
    "retirada": "Retirada combinada",
    "entrega_combinada": "Entrega combinada",
}
PAGAMENTO_STATUS = {
    "nao_iniciado": "Pagamento não iniciado",
    "aguardando": "Aguardando pagamento",
    "pendente": "Pagamento em análise",
    "aprovado": "Pagamento aprovado",
    "rejeitado": "Pagamento não aprovado",
    "cancelado": "Pagamento cancelado",
    "reembolsado": "Pagamento reembolsado",
}
DENUNCIA_MOTIVOS = {
    "golpe": "Suspeita de golpe",
    "proibido": "Produto ou serviço proibido",
    "enganoso": "Informação enganosa",
    "duplicado": "Anúncio duplicado",
    "ofensivo": "Conteúdo ofensivo",
    "outro": "Outro motivo",
}
COMUNICADO_TIPOS = {
    "informacao": "Informação",
    "atencao": "Atenção",
    "novidade": "Novidade",
}
PROBLEMA_MOTIVOS = {
    "PRODUTO_NAO_ENTREGUE": "Produto não entregue",
    "COMPRADOR_DESISTIU": "Comprador desistiu",
    "PRODUTO_DIFERENTE_DO_ANUNCIADO": "Produto diferente do anunciado",
    "PAGAMENTO_NAO_COMBINADO": "Pagamento não combinado",
    "VENDEDOR_NAO_RESPONDE": "Vendedor não responde",
    "COMPRADOR_NAO_RESPONDE": "Comprador não responde",
    "OUTRO": "Outro",
}
LOGIN_MAX_FALHAS = 5
LOGIN_JANELA_SEGUNDOS = 15 * 60


def validar_configuracao_producao():
    if FLASK_ENV != "production":
        return
    obrigatorias = (
        "CLOUDINARY_URL",
        "ADMIN_PASSWORD",
        "ADMIN_WHATSAPP",
        "PIX_KEY",
        "SUPPORT_WHATSAPP",
    )
    ausentes = [nome for nome in obrigatorias if not os.environ.get(nome, "").strip()]
    if not any(
        os.environ.get(nome, "").strip()
        for nome in ("DATABASE_URL", "RESTORED_DATABASE_URL")
    ):
        ausentes.insert(0, "DATABASE_URL")
    if ausentes:
        raise RuntimeError(
            "Configuracao de producao incompleta. Defina: " + ", ".join(ausentes)
        )


def limpar_whatsapp(valor):
    return re.sub(r"\D", "", valor or "")


def chave_tentativa_login(username):
    origem = request.remote_addr or "desconhecida"
    conteudo = f"{origem}|{(username or '').strip().lower()}".encode("utf-8")
    return hmac.new(
        app.secret_key.encode("utf-8"), conteudo, hashlib.sha256
    ).hexdigest()


def login_temporariamente_bloqueado(db, chave, agora=None):
    agora = int(agora or time.time())
    linha = db.execute(
        "SELECT bloqueado_ate FROM tentativas_login WHERE chave=?", (chave,)
    ).fetchone()
    return bool(linha and int(linha["bloqueado_ate"] or 0) > agora)


def registrar_falha_login(db, chave, agora=None):
    agora = int(agora or time.time())
    linha = db.execute(
        "SELECT falhas, janela_inicio FROM tentativas_login WHERE chave=?", (chave,)
    ).fetchone()
    if not linha:
        db.execute(
            "INSERT INTO tentativas_login (chave, falhas, janela_inicio, bloqueado_ate) VALUES (?,?,?,0)",
            (chave, 1, agora),
        )
    elif agora - int(linha["janela_inicio"]) >= LOGIN_JANELA_SEGUNDOS:
        db.execute(
            "UPDATE tentativas_login SET falhas=1, janela_inicio=?, bloqueado_ate=0 WHERE chave=?",
            (agora, chave),
        )
    else:
        falhas = int(linha["falhas"]) + 1
        bloqueado_ate = (
            agora + LOGIN_JANELA_SEGUNDOS if falhas >= LOGIN_MAX_FALHAS else 0
        )
        db.execute(
            "UPDATE tentativas_login SET falhas=?, bloqueado_ate=? WHERE chave=?",
            (falhas, bloqueado_ate, chave),
        )
    db.execute(
        "DELETE FROM tentativas_login WHERE janela_inicio<? AND bloqueado_ate<?",
        (agora - 86400, agora),
    )
    db.commit()


def categoria_label(valor):
    return CATEGORIA_CANONICA.get(valor, valor)


def pedido_status_label(valor):
    return PEDIDO_STATUS.get(valor, valor)


def pedido_entrega_label(valor):
    return PEDIDO_ENTREGA.get(valor, valor)


def pagamento_status_label(valor):
    return PAGAMENTO_STATUS.get(valor, valor)


def foto_url(foto, largura=1200):
    if not foto:
        return ""
    if foto.startswith(("http://", "https://")):
        if "res.cloudinary.com" in foto and "/upload/" in foto:
            transformacao = f"f_auto,q_auto,c_limit,w_{int(largura)}"
            return foto.replace("/upload/", f"/upload/{transformacao}/", 1)
        return foto
    return url_for("uploaded_file", filename=foto)


def nome_loja_publica(usuario):
    return (usuario["loja_nome"] or usuario["nome"]).strip()


def slug_loja(nome):
    texto = unicodedata.normalize("NFKD", nome or "")
    texto = texto.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", texto).strip("-")[:80] or "loja"


def normalizar_busca_loja(texto):
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = texto.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"\s+", " ", texto).strip()


def url_publica(endpoint, **valores):
    valores["_external"] = True
    if FLASK_ENV == "production":
        valores["_scheme"] = "https"
    return url_for(endpoint, **valores)


def url_loja_publica(usuario, externa=False):
    valores = {
        "loja_id": usuario["id"],
        "slug": slug_loja(nome_loja_publica(usuario)),
    }
    if externa:
        return url_publica("loja_publica", **valores)
    return url_for("loja_publica", **valores)


def url_loja_publica_por_dados(usuario_id, loja_nome, nome):
    return url_loja_publica({"id": usuario_id, "loja_nome": loja_nome, "nome": nome})


def reservar_selo_fundador(db):
    if not LIMITE_FUNDADORES:
        return 0, None
    if USE_PG:
        db.execute("LOCK TABLE usuarios IN SHARE ROW EXCLUSIVE MODE")
    else:
        db.execute("BEGIN IMMEDIATE")
    total = db.execute(
        "SELECT COUNT(*) FROM usuarios WHERE fundador_origem='automatico'"
    ).fetchone()[0]
    if total >= LIMITE_FUNDADORES:
        return 0, None
    return 1, "automatico"


def plano_valido(usuario):
    if not usuario or not usuario["plano_ativo"]:
        return False
    expira = usuario["plano_expira"]
    if not expira:
        return True
    if isinstance(expira, date):
        data_expiracao = expira
    else:
        try:
            data_expiracao = date.fromisoformat(str(expira)[:10])
        except ValueError:
            return False
    return data_expiracao >= date.today()


def arquivo_e_imagem_valida(arquivo, extensao):
    inicio = arquivo.stream.read(16)
    arquivo.stream.seek(0)
    if extensao in {"jpg", "jpeg"}:
        return inicio.startswith(bytes.fromhex("ffd8ff"))
    if extensao == "png":
        return inicio.startswith(bytes.fromhex("89504e470d0a1a0a"))
    if extensao == "webp":
        return len(inicio) >= 12 and inicio[:4] == b"RIFF" and inicio[8:12] == b"WEBP"
    return False


def normalizar_preco(valor):
    texto = (valor or "").strip().replace("R$", "").replace(" ", "")
    if not texto or not re.fullmatch(r"[0-9.,]+", texto):
        return None
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif texto.count(".") > 1 or (
        texto.count(".") == 1 and len(texto.rsplit(".", 1)[1]) == 3
    ):
        texto = texto.replace(".", "")
    try:
        numero = Decimal(texto)
    except InvalidOperation:
        return None
    if numero <= 0 or numero > Decimal("999999999.99"):
        return None
    numero = numero.quantize(Decimal("0.01"))
    inteiro, centavos = f"{numero:.2f}".split(".")
    inteiro = f"{int(inteiro):,}".replace(",", ".")
    return f"{inteiro},{centavos}"


def preco_decimal(valor):
    texto = str(valor or "").replace(".", "").replace(",", ".")
    try:
        return Decimal(texto).quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise ValueError("Preco invalido") from exc


def validar_usuario(nome, username, senha, whatsapp):
    if len(nome) < 3:
        return "Informe um nome com pelo menos 3 caracteres."
    if not USERNAME_RE.fullmatch(username):
        return "Nome de usuário inválido. Use 3 a 24 caracteres com letras, números ou underscore."
    if len(senha) < 8:
        return "Use uma senha com pelo menos 8 caracteres."
    whatsapp_limpo = limpar_whatsapp(whatsapp)
    if len(whatsapp_limpo) not in {10, 11}:
        return "WhatsApp inválido. Informe DDD + número."
    return None


def validar_anuncio(titulo, descricao, preco, categoria, condicao, bairro):
    if len(titulo) < 4:
        return "Titulo muito curto."
    if len(descricao) < 10:
        return "Descricao muito curta."
    if not preco or len(preco) > 20:
        return "Informe um preço válido."
    if categoria not in CATEGORIAS:
        return "Categoria invalida."
    if condicao not in {"Novo", "Seminovo", "Usado"}:
        return "Condicao invalida."
    if len(bairro) < 2 or len(bairro) > 60 or any(ord(char) < 32 for char in bairro):
        return "Informe um bairro válido em Colatina."
    return None


def validar_estoque(valor, minimo=1):
    try:
        estoque = int(str(valor).strip() or "1")
    except ValueError:
        return None, "Informe uma quantidade valida."
    if estoque < minimo or estoque > 999:
        if minimo == 0:
            return None, "A quantidade deve ficar entre 0 e 999."
        return None, "A quantidade deve ficar entre 1 e 999."
    return estoque, None


def converter_data_hora(valor):
    if isinstance(valor, datetime):
        return valor
    if not valor:
        return None
    try:
        return datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
    except ValueError:
        return None


def formatar_duracao_media(segundos):
    if segundos is None:
        return "Sem dados ainda"
    minutos = max(0, round(segundos / 60))
    if minutos < 60:
        return f"{minutos} min"
    horas = minutos // 60
    if horas < 24:
        return f"{horas}h {minutos % 60}min"
    dias = horas // 24
    return f"{dias} dia{'s' if dias != 1 else ''}"


def formatar_data_reputacao(valor, incluir_hora=False):
    data = converter_data_hora(valor)
    if not data:
        return "Ainda não registrado" if incluir_hora else "Não informado"
    formato = "%d/%m/%Y às %H:%M" if incluir_hora else "%d/%m/%Y"
    return data.strftime(formato)


def formatar_data_cockpit(valor):
    data = converter_data_hora(valor)
    if not data:
        return "Data não informada"
    return data.strftime("%d/%m/%Y · %H:%M")


def contar_testes_automatizados():
    valor_ambiente = os.environ.get("CI_TEST_COUNT", "").strip()
    if valor_ambiente.isdigit():
        return int(valor_ambiente)

    diretorio_testes = os.path.join(BASE_DIR, "tests")
    total = 0
    try:
        for raiz, _, arquivos in os.walk(diretorio_testes):
            for nome_arquivo in arquivos:
                if not nome_arquivo.startswith("test_") or not nome_arquivo.endswith(
                    ".py"
                ):
                    continue
                caminho = os.path.join(raiz, nome_arquivo)
                with open(caminho, encoding="utf-8") as arquivo:
                    total += sum(
                        1
                        for linha in arquivo
                        if re.match(r"\s+def test_[a-zA-Z0-9_]+\(", linha)
                    )
    except OSError:
        return None
    return total or None


def _duracao_em_segundos(inicio_valor, fim_valor):
    inicio = converter_data_hora(inicio_valor)
    fim = converter_data_hora(fim_valor)
    if not inicio or not fim:
        return None
    if inicio.tzinfo is not None and fim.tzinfo is None:
        inicio = inicio.replace(tzinfo=None)
    elif fim.tzinfo is not None and inicio.tzinfo is None:
        fim = fim.replace(tzinfo=None)
    return max(0, (fim - inicio).total_seconds())


def calcular_reputacoes_usuarios(db, usuarios):
    """Calcula reputação em lote, sem armazenar contadores editáveis."""
    usuarios = list(usuarios)
    if not usuarios:
        return {}

    reputacoes = {}
    for usuario in usuarios:
        base = {
            "membro_desde": formatar_data_reputacao(usuario["criado_em"]),
            "ultimo_acesso": formatar_data_reputacao(
                usuario["ultimo_acesso_em"], incluir_hora=True
            ),
            "loja_verificada": bool(usuario["loja_verificada"]),
        }
        reputacoes[usuario["id"]] = {
            "vendedor": {
                **base,
                "vendas_concluidas": 0,
                "pedidos_concluidos": 0,
                "pedidos_cancelados": 0,
                "pedidos_em_analise": 0,
                "taxa_conclusao": 0,
                "tempo_medio_conclusao": "Sem dados ainda",
            },
            "comprador": {
                **base,
                "compras_concluidas": 0,
                "compras_canceladas": 0,
                "pedidos_em_analise": 0,
                "taxa_conclusao": 0,
                "tempo_medio_recebimento": "Sem dados ainda",
            },
        }

    ids = [usuario["id"] for usuario in usuarios]
    marcadores = ",".join("?" for _ in ids)
    pedidos = db.execute(
        "SELECT p.vendedor_id, p.comprador_id, p.status, p.criado_em, "
        "p.atualizado_em, p.comprador_confirmou_em, "
        "COALESCE(conclusao.criado_em, p.atualizado_em) AS concluido_em "
        "FROM pedidos p "
        "LEFT JOIN pedido_eventos conclusao ON conclusao.pedido_id=p.id "
        "AND conclusao.tipo='PEDIDO_CONCLUIDO' "
        f"WHERE p.vendedor_id IN ({marcadores}) OR p.comprador_id IN ({marcadores})",
        tuple(ids + ids),
    ).fetchall()

    duracoes_vendedor = {usuario_id: [] for usuario_id in ids}
    duracoes_comprador = {usuario_id: [] for usuario_id in ids}
    for pedido in pedidos:
        vendedor_id = pedido["vendedor_id"]
        comprador_id = pedido["comprador_id"]
        status = pedido["status"]
        if vendedor_id in reputacoes:
            indicador = reputacoes[vendedor_id]["vendedor"]
            if status == "concluido":
                indicador["vendas_concluidas"] += 1
                indicador["pedidos_concluidos"] += 1
                duracao = _duracao_em_segundos(
                    pedido["criado_em"], pedido["concluido_em"]
                )
                if duracao is not None:
                    duracoes_vendedor[vendedor_id].append(duracao)
            elif status in {"cancelado", "recusado"}:
                indicador["pedidos_cancelados"] += 1
            elif status == "em_analise":
                indicador["pedidos_em_analise"] += 1

        if comprador_id in reputacoes:
            indicador = reputacoes[comprador_id]["comprador"]
            if status == "concluido":
                indicador["compras_concluidas"] += 1
                duracao = _duracao_em_segundos(
                    pedido["criado_em"], pedido["comprador_confirmou_em"]
                )
                if duracao is not None:
                    duracoes_comprador[comprador_id].append(duracao)
            elif status in {"cancelado", "recusado"}:
                indicador["compras_canceladas"] += 1
            elif status == "em_analise":
                indicador["pedidos_em_analise"] += 1

    for usuario_id, reputacao in reputacoes.items():
        vendedor = reputacao["vendedor"]
        finalizados = vendedor["pedidos_concluidos"] + vendedor["pedidos_cancelados"]
        vendedor["taxa_conclusao"] = (
            round(vendedor["pedidos_concluidos"] * 100 / finalizados)
            if finalizados
            else 0
        )
        duracoes = duracoes_vendedor[usuario_id]
        vendedor["tempo_medio_conclusao"] = formatar_duracao_media(
            sum(duracoes) / len(duracoes) if duracoes else None
        )

        comprador = reputacao["comprador"]
        finalizados = comprador["compras_concluidas"] + comprador["compras_canceladas"]
        comprador["taxa_conclusao"] = (
            round(comprador["compras_concluidas"] * 100 / finalizados)
            if finalizados
            else 0
        )
        duracoes = duracoes_comprador[usuario_id]
        comprador["tempo_medio_recebimento"] = formatar_duracao_media(
            sum(duracoes) / len(duracoes) if duracoes else None
        )
    return reputacoes


def calcular_reputacao_usuario(db, usuario):
    return calcular_reputacoes_usuarios(db, [usuario])[usuario["id"]]


def validar_perfil_loja(nome, descricao, bairro, whatsapp):
    if nome and (len(nome) < 3 or len(nome) > 60):
        return "O nome da loja deve ter entre 3 e 60 caracteres."
    if nome and any(ord(char) < 32 for char in nome):
        return "Informe um nome de loja válido."
    if len(descricao) > 600:
        return "A descrição da loja deve ter no máximo 600 caracteres."
    if bairro and (len(bairro) < 2 or len(bairro) > 60):
        return "Informe um bairro válido."
    if whatsapp and len(limpar_whatsapp(whatsapp)) not in {10, 11}:
        return "Informe um WhatsApp comercial com DDD."
    return None


def csrf_token():
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_hex(16)
        session["_csrf_token"] = token
    return token


def salvar_tokens_mercadopago(db, usuario_id, dados):
    access_token = dados.get("access_token")
    refresh_token = dados.get("refresh_token")
    mp_user_id = dados.get("user_id")
    if not access_token or not refresh_token or not mp_user_id:
        raise MercadoPagoError("Autorizacao incompleta do Mercado Pago.")
    expira_em = datetime.now(timezone.utc) + timedelta(
        seconds=int(dados.get("expires_in") or 15552000)
    )
    db.execute(
        "UPDATE usuarios SET mp_access_token=?, mp_refresh_token=?, mp_user_id=?, "
        "mp_token_expira=?, mp_conectado_em=CURRENT_TIMESTAMP WHERE id=?",
        (
            criptografar_token(access_token, app.secret_key),
            criptografar_token(refresh_token, app.secret_key),
            str(mp_user_id),
            expira_em.isoformat(),
            usuario_id,
        ),
    )
    db.commit()


def registrar_status_email_pedido(db, pedido_id, email_status):
    db.execute(
        "UPDATE pedidos SET admin_email_status=?, "
        "admin_email_enviado_em=CASE WHEN ?='enviado' THEN CURRENT_TIMESTAMP ELSE admin_email_enviado_em END "
        "WHERE id=?",
        (email_status, email_status, pedido_id),
    )


def papel_usuario_pedido(pedido, usuario_id, e_admin=False):
    if e_admin:
        return "administrador"
    if pedido["comprador_id"] == usuario_id:
        return "comprador"
    if pedido["vendedor_id"] == usuario_id:
        return "vendedor"
    return "sistema"


def registrar_evento_pedido(
    db,
    pedido_id,
    tipo,
    descricao,
    usuario_id=None,
    papel_usuario="sistema",
    estado_anterior=None,
    estado_posterior=None,
    dados_adicionais=None,
):
    dados = json.dumps(
        dados_adicionais or {}, ensure_ascii=False, separators=(",", ":")
    )
    return db.execute(
        "INSERT INTO pedido_eventos "
        "(pedido_id, tipo, usuario_id, papel_usuario, descricao, dados_adicionais, "
        "estado_anterior, estado_posterior) VALUES (?,?,?,?,?,?,?,?) "
        "ON CONFLICT (pedido_id, tipo) DO NOTHING",
        (
            pedido_id,
            tipo,
            usuario_id,
            papel_usuario,
            descricao,
            dados,
            estado_anterior,
            estado_posterior,
        ),
    )


def buscar_eventos_pedidos(db, pedidos_lista):
    ids = [pedido["id"] for pedido in pedidos_lista]
    eventos_por_pedido = {pedido_id: [] for pedido_id in ids}
    if not ids:
        return eventos_por_pedido
    marcadores = ",".join("?" for _ in ids)
    eventos = db.execute(
        "SELECT e.*, u.nome AS usuario_nome FROM pedido_eventos e "
        "LEFT JOIN usuarios u ON u.id=e.usuario_id "
        f"WHERE e.pedido_id IN ({marcadores}) "
        "ORDER BY e.criado_em ASC, e.id ASC",
        tuple(ids),
    ).fetchall()
    for evento in eventos:
        eventos_por_pedido[evento["pedido_id"]].append(evento)
    return eventos_por_pedido


def buscar_pedido_admin(db, pedido_id):
    return db.execute(
        "SELECT p.*, a.titulo, comprador.nome AS comprador_nome, "
        "vendedor.nome AS vendedor_nome "
        "FROM pedidos p "
        "JOIN anuncios a ON a.id=p.anuncio_id "
        "JOIN usuarios comprador ON comprador.id=p.comprador_id "
        "JOIN usuarios vendedor ON vendedor.id=p.vendedor_id "
        "WHERE p.id=?",
        (pedido_id,),
    ).fetchone()


def obter_token_vendedor(usuario_id):
    db = get_db()
    usuario = db.execute(
        "SELECT mp_access_token, mp_refresh_token, mp_token_expira FROM usuarios WHERE id=?",
        (usuario_id,),
    ).fetchone()
    if not usuario or not usuario["mp_access_token"]:
        raise MercadoPagoError("O vendedor ainda nao conectou o Mercado Pago.")

    access_token = descriptografar_token(usuario["mp_access_token"], app.secret_key)
    expira = usuario["mp_token_expira"]
    if expira:
        try:
            data_expira = datetime.fromisoformat(str(expira).replace("Z", "+00:00"))
            if data_expira.tzinfo is None:
                data_expira = data_expira.replace(tzinfo=timezone.utc)
        except ValueError:
            data_expira = datetime.now(timezone.utc)
        if data_expira <= datetime.now(timezone.utc) + timedelta(days=1):
            refresh_token = descriptografar_token(
                usuario["mp_refresh_token"], app.secret_key
            )
            novos_dados = renovar_token(refresh_token)
            salvar_tokens_mercadopago(db, usuario_id, novos_dados)
            access_token = novos_dados["access_token"]
    return access_token


def atualizar_pagamento_do_pedido(db, pagamento):
    referencia = str(pagamento.get("external_reference") or "")
    correspondencia = re.fullmatch(r"MC-PEDIDO-(\d+)", referencia)
    if not correspondencia:
        return False
    pedido_id = int(correspondencia.group(1))
    pedido = db.execute(
        "SELECT p.*, u.mp_user_id FROM pedidos p "
        "JOIN usuarios u ON u.id=p.vendedor_id WHERE p.id=?",
        (pedido_id,),
    ).fetchone()
    if not pedido:
        return False

    collector_id = str(pagamento.get("collector_id") or "")
    if pedido["mp_user_id"] and collector_id != str(pedido["mp_user_id"]):
        return False
    try:
        valor_pago = Decimal(str(pagamento.get("transaction_amount"))).quantize(
            Decimal("0.01")
        )
    except (InvalidOperation, TypeError):
        return False
    if valor_pago != preco_decimal(pedido["valor"]):
        return False

    status_mp = str(pagamento.get("status") or "")
    mapa_status = {
        "approved": "aprovado",
        "pending": "pendente",
        "in_process": "pendente",
        "rejected": "rejeitado",
        "cancelled": "cancelado",
        "refunded": "reembolsado",
        "charged_back": "reembolsado",
    }
    status_local = mapa_status.get(status_mp, "pendente")
    db.execute(
        "UPDATE pedidos SET pagamento_status=?, mp_payment_id=?, atualizado_em=CURRENT_TIMESTAMP WHERE id=?",
        (status_local, str(pagamento.get("id") or ""), pedido_id),
    )
    db.commit()
    return True


def pode_criar_anuncio(usuario_id):
    db = get_db()
    usuario = db.execute(
        "SELECT plano_ativo, plano_expira, is_admin FROM usuarios WHERE id=?",
        (usuario_id,),
    ).fetchone()
    if usuario["is_admin"] or plano_valido(usuario):
        return True, None

    if usuario["plano_ativo"]:
        db.execute(
            "UPDATE usuarios SET plano_ativo=0, plano_expira=NULL WHERE id=?",
            (usuario_id,),
        )
        db.commit()

    total = db.execute(
        "SELECT COUNT(*) FROM anuncios WHERE usuario_id=? AND ativo=1",
        (usuario_id,),
    ).fetchone()[0]
    if total < LIMITE_GRATIS:
        restam = LIMITE_GRATIS - total
        return True, f"Você tem {restam} anúncio(s) gratuito(s) restante(s)."
    return False, "limite"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def logado():
    return session.get("usuario_id")


def admin():
    return session.get("is_admin", False)


def listar_lojas_administradas(usuario_id=None):
    """Retorna apenas as lojas proprias ou explicitamente vinculadas ao gestor."""
    usuario_id = usuario_id or session.get("usuario_id")
    if not usuario_id:
        return []
    return list(
        get_db()
        .execute(
            "SELECT u.id, u.nome, u.username, u.loja_nome, u.loja_descricao, "
            "u.loja_bairro, u.loja_verificada, u.fundador, "
            "(SELECT COUNT(*) FROM anuncios a WHERE a.usuario_id=u.id) AS total_anuncios, "
            "(SELECT COUNT(*) FROM anuncios a WHERE a.usuario_id=u.id AND a.ativo=1 "
            "AND a.estoque>0) AS anuncios_ativos, "
            "COALESCE((SELECT SUM(a.visualizacoes) FROM anuncios a "
            "WHERE a.usuario_id=u.id), 0) AS total_visualizacoes "
            "FROM usuarios u WHERE u.ativo=1 AND (u.id=? OR EXISTS ("
            "SELECT 1 FROM loja_administradores la "
            "WHERE la.administrador_id=? AND la.loja_id=u.id)) "
            "ORDER BY CASE WHEN u.id=? THEN 0 ELSE 1 END, "
            "COALESCE(u.loja_nome, u.nome)",
            (usuario_id, usuario_id, usuario_id),
        )
        .fetchall()
    )


def pode_administrar_loja(loja_id, usuario_id=None):
    usuario_id = usuario_id or session.get("usuario_id")
    if not usuario_id:
        return False
    if int(loja_id) == int(usuario_id) or admin():
        return True
    vinculo = (
        get_db()
        .execute(
            "SELECT 1 FROM loja_administradores WHERE administrador_id=? AND loja_id=?",
            (usuario_id, loja_id),
        )
        .fetchone()
    )
    return bool(vinculo)


def loja_ativa_id():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return None
    ids_permitidos = {loja["id"] for loja in listar_lojas_administradas(usuario_id)}
    escolhida = session.get("loja_ativa_id")
    if escolhida in ids_permitidos:
        return escolhida
    session["loja_ativa_id"] = usuario_id
    return usuario_id


validar_configuracao_producao()


with app.app_context():
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    init_db()


app.teardown_appcontext(close_db)
app.jinja_env.globals["csrf_token"] = csrf_token
app.jinja_env.globals["categoria_label"] = categoria_label
app.jinja_env.globals["plano_valido"] = plano_valido
app.jinja_env.globals["foto_url"] = foto_url
app.jinja_env.globals["url_loja_publica"] = url_loja_publica
app.jinja_env.globals["url_loja_publica_por_dados"] = url_loja_publica_por_dados
app.jinja_env.globals["pedido_status_label"] = pedido_status_label
app.jinja_env.globals["pedido_entrega_label"] = pedido_entrega_label
app.jinja_env.globals["pagamento_status_label"] = pagamento_status_label
app.jinja_env.globals["mercadopago_configurado"] = mercadopago_configurado
app.jinja_env.globals["mercadopago_pagamentos_configurados"] = (
    mercadopago_pagamentos_configurados
)
app.jinja_env.globals["neo_configurado"] = neo_configurado
app.jinja_env.globals["pode_administrar_loja"] = pode_administrar_loja


@app.context_processor
def fornecer_contexto_multiloja():
    if not logado():
        return {"lojas_administradas": [], "loja_ativa_nav": None}
    lojas = listar_lojas_administradas()
    ativa_id = loja_ativa_id()
    ativa = next((loja for loja in lojas if loja["id"] == ativa_id), None)
    return {"lojas_administradas": lojas, "loja_ativa_nav": ativa}


@app.before_request
def registrar_acesso_publico():
    """Conta uma visita por sessao, sem guardar IP ou identificar o visitante."""
    endpoints_ignorados = {"static", "health", "robots", "sitemap"}
    if (
        request.method != "GET"
        or request.endpoint in endpoints_ignorados
        or session.get("_visita_registrada")
    ):
        return

    user_agent = (request.user_agent.string or "").lower()
    marcadores_de_robo = (
        "bot",
        "crawler",
        "spider",
        "slurp",
        "facebookexternalhit",
        "whatsapp",
        "linkedinbot",
        "twitterbot",
    )
    if any(marcador in user_agent for marcador in marcadores_de_robo):
        return

    db = get_db()
    db.execute(
        "UPDATE estatisticas SET valor = valor + 1 WHERE chave=?",
        ("acessos_site",),
    )
    db.commit()
    session["_visita_registrada"] = True


@app.context_processor
def fornecer_total_acessos():
    try:
        linha = (
            get_db()
            .execute(
                "SELECT valor FROM estatisticas WHERE chave=?",
                ("acessos_site",),
            )
            .fetchone()
        )
        total = int(linha[0]) if linha else 0
    except Exception:
        app.logger.exception("Falha ao consultar o contador de acessos")
        total = 0

    return {
        "total_acessos": total,
        "total_acessos_formatado": f"{total:,}".replace(",", "."),
    }


@app.context_processor
def fornecer_comunicado_global():
    try:
        comunicado = (
            get_db()
            .execute(
                "SELECT id, titulo, mensagem, tipo, criado_em "
                "FROM comunicados WHERE ativo=1 "
                "ORDER BY criado_em DESC, id DESC LIMIT 1"
            )
            .fetchone()
        )
    except Exception:
        app.logger.exception("Falha ao consultar comunicado global")
        comunicado = None
    return {"comunicado_global": comunicado}


@app.before_request
def atualizar_usuario_da_sessao():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return
    usuario = (
        get_db()
        .execute(
            "SELECT id, nome, username, is_admin, ativo FROM usuarios WHERE id=?",
            (usuario_id,),
        )
        .fetchone()
    )
    if not usuario or not usuario["ativo"]:
        session.clear()
        return
    session["usuario_nome"] = usuario["nome"]
    session["usuario_username"] = usuario["username"]
    session["is_admin"] = bool(usuario["is_admin"])


@app.after_request
def adicionar_cabecalhos_seguranca(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
    )
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self' data: https://res.cloudinary.com; style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; object-src 'none'; frame-ancestors 'none'; "
        "base-uri 'self'; form-action 'self'",
    )
    if request.is_secure:
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )
    return response


@app.before_request
def proteger_formularios():
    if request.method == "POST" and request.endpoint != "mercadopago_webhook":
        token_sessao = session.get("_csrf_token")
        token_form = request.form.get("csrf_token")
        if (
            not token_sessao
            or not token_form
            or not secrets.compare_digest(token_sessao, token_form)
        ):
            abort(400)


@app.route("/")
def index():
    db = get_db()
    busca = request.args.get("q", "").strip()[:100]
    categoria = request.args.get("categoria", "")
    if categoria and categoria not in CATEGORIA_ALIASES:
        categoria = ""

    query = (
        "SELECT a.*, u.nome AS vendedor_nome, u.loja_nome, u.whatsapp "
        "FROM anuncios a "
        "JOIN usuarios u ON a.usuario_id = u.id "
        "WHERE a.ativo = 1 AND a.estoque > 0"
    )
    params = []
    if busca:
        query += (
            " AND (LOWER(COALESCE(a.titulo, '')) LIKE LOWER(?) "
            "OR LOWER(COALESCE(a.descricao, '')) LIKE LOWER(?) "
            "OR LOWER(COALESCE(a.bairro, '')) LIKE LOWER(?))"
        )
        params += [f"%{busca}%", f"%{busca}%", f"%{busca}%"]
    if categoria:
        aliases = CATEGORIA_ALIASES[categoria]
        marcadores = ",".join("?" for _ in aliases)
        query += f" AND a.categoria IN ({marcadores})"
        params.extend(aliases)
    query += " ORDER BY a.criado_em DESC"
    anuncios = db.execute(query, params).fetchall()

    lojas_linhas = db.execute(
        "WITH catalogo AS ("
        "SELECT usuario_id, COUNT(*) AS total_anuncios, "
        "COALESCE(SUM(COALESCE(visualizacoes, 0)), 0) AS total_visualizacoes "
        "FROM anuncios WHERE ativo=1 AND estoque>0 GROUP BY usuario_id"
        "), vendas AS ("
        "SELECT vendedor_id, COUNT(*) AS vendas_concluidas FROM pedidos "
        "WHERE status='concluido' GROUP BY vendedor_id"
        ") SELECT u.id, u.nome, u.loja_nome, u.loja_bairro, "
        "u.loja_verificada, u.fundador, u.criado_em, c.total_anuncios, "
        "c.total_visualizacoes, COALESCE(v.vendas_concluidas, 0) AS vendas_concluidas "
        "FROM usuarios u JOIN catalogo c ON c.usuario_id=u.id "
        "LEFT JOIN vendas v ON v.vendedor_id=u.id WHERE u.ativo=1 "
        "ORDER BY CASE WHEN u.id=? THEN 0 ELSE 1 END, "
        "u.loja_verificada DESC, c.total_anuncios DESC, "
        "c.total_visualizacoes DESC, u.id ASC",
        (LOJA_OFICIAL_ID,),
    ).fetchall()
    lojas_destaque = []
    for loja in lojas_linhas:
        nome_publico = nome_loja_publica(loja)
        palavras_nome = [palavra for palavra in nome_publico.split() if palavra]
        lojas_destaque.append(
            {
                "id": loja["id"],
                "nome": loja["nome"],
                "loja_nome": loja["loja_nome"],
                "nome_publico": nome_publico,
                "logo_iniciais": "".join(
                    palavra[0] for palavra in palavras_nome[:2]
                ).upper()
                or "MC",
                "bairro": loja["loja_bairro"],
                "loja_verificada": loja["loja_verificada"],
                "fundador": loja["fundador"],
                "loja_oficial": loja["id"] == LOJA_OFICIAL_ID,
                "membro_desde": formatar_data_reputacao(loja["criado_em"]),
                "total_anuncios": loja["total_anuncios"],
                "total_visualizacoes": loja["total_visualizacoes"],
                "vendas_concluidas": loja["vendas_concluidas"],
            }
        )

    info_plano = None
    if session.get("usuario_id"):
        usuario = db.execute(
            "SELECT plano_ativo, plano_expira, is_admin FROM usuarios WHERE id=?",
            (session["usuario_id"],),
        ).fetchone()
        if not usuario["is_admin"] and not plano_valido(usuario):
            total = db.execute(
                "SELECT COUNT(*) FROM anuncios WHERE usuario_id=? AND ativo=1",
                (session["usuario_id"],),
            ).fetchone()[0]
            restam = max(0, LIMITE_GRATIS - total)
            info_plano = {"restam": restam, "limite": LIMITE_GRATIS}

    return render_template(
        "index.html",
        anuncios=anuncios,
        lojas_destaque=lojas_destaque,
        categorias=CATEGORIAS,
        busca=busca,
        cat_sel=categoria,
        info_plano=info_plano,
        valor_plano=VALOR_PLANO,
        limite_gratis=LIMITE_GRATIS,
        mercado_livre_afiliado_url=MERCADO_LIVRE_AFILIADO_URL,
        ofertas_parceiros=OFERTAS_PARCEIROS_HOME,
        site_url=url_publica("index"),
        imagem_social=url_publica("static", filename="mercado-colatina-social.svg"),
    )


@app.route("/health")
def health():
    try:
        get_db().execute("SELECT 1").fetchone()
    except Exception:
        app.logger.exception("Falha na verificacao de saude do banco")
        return {"status": "indisponivel"}, 503
    return {"status": "ok"}, 200


@app.route("/robots.txt")
def robots():
    conteudo = (
        f"User-agent: *\nAllow: /\nSitemap: {url_for('sitemap', _external=True)}\n"
    )
    return Response(conteudo, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    endpoints = [
        "index",
        "cadastro",
        "login",
        "pagina_seguranca",
        "pagina_ajuda",
        "pagina_privacidade",
        "pagina_termos",
    ]
    urls = "".join(
        f"<url><loc>{url_for(endpoint, _external=True)}</loc></url>"
        for endpoint in endpoints
    )
    lojas = (
        get_db()
        .execute(
            "SELECT DISTINCT u.id, u.nome, u.loja_nome FROM usuarios u "
            "JOIN anuncios a ON a.usuario_id=u.id "
            "WHERE u.ativo=1 AND a.ativo=1 AND a.estoque>0"
        )
        .fetchall()
    )
    urls += "".join(
        f"<url><loc>{url_loja_publica(loja, externa=True)}</loc></url>"
        for loja in lojas
    )
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    return Response(xml, mimetype="application/xml")


@app.route("/loja/<int:loja_id>")
def loja_publica_por_id(loja_id):
    loja = (
        get_db()
        .execute(
            "SELECT id, nome, loja_nome FROM usuarios WHERE id=? AND ativo=1",
            (loja_id,),
        )
        .fetchone()
    )
    if not loja:
        abort(404)
    return redirect(url_loja_publica(loja), code=301)


@app.route("/loja/<int:loja_id>-<slug>")
def loja_publica(loja_id, slug):
    db = get_db()
    loja = db.execute(
        "SELECT id, nome, loja_nome, loja_descricao, loja_bairro, loja_whatsapp, "
        "criado_em, ultimo_acesso_em, loja_verificada, fundador, fundador_desde "
        "FROM usuarios WHERE id=? AND ativo=1",
        (loja_id,),
    ).fetchone()
    if not loja:
        abort(404)

    nome_publico = nome_loja_publica(loja)
    slug_canonico = slug_loja(nome_publico)
    if slug != slug_canonico:
        return redirect(url_loja_publica(loja), code=301)

    anuncios_ativos = list(
        db.execute(
            "SELECT * FROM anuncios WHERE usuario_id=? AND ativo=1 AND estoque>0 "
            "ORDER BY criado_em DESC, id DESC",
            (loja_id,),
        ).fetchall()
    )

    busca = request.args.get("q", "").strip()[:100]
    categoria = request.args.get("categoria", "").strip()
    if categoria not in CATEGORIAS:
        categoria = ""
    preco_minimo_texto = request.args.get("preco_min", "").strip()[:20]
    preco_maximo_texto = request.args.get("preco_max", "").strip()[:20]
    ordem = request.args.get("ordem", "recentes")
    ordens_validas = {"recentes", "mais_vistos", "menor_preco", "maior_preco"}
    if ordem not in ordens_validas:
        ordem = "recentes"

    preco_minimo_normalizado = normalizar_preco(preco_minimo_texto)
    preco_maximo_normalizado = normalizar_preco(preco_maximo_texto)
    preco_minimo = (
        preco_decimal(preco_minimo_normalizado) if preco_minimo_normalizado else None
    )
    preco_maximo = (
        preco_decimal(preco_maximo_normalizado) if preco_maximo_normalizado else None
    )
    termo_busca = normalizar_busca_loja(busca)

    anuncios = list(anuncios_ativos)
    if termo_busca:
        anuncios = [
            anuncio
            for anuncio in anuncios
            if termo_busca
            in normalizar_busca_loja(f"{anuncio['titulo']} {anuncio['descricao']}")
        ]
    if categoria:
        anuncios = [
            anuncio
            for anuncio in anuncios
            if categoria_label(anuncio["categoria"]) == categoria
        ]
    if preco_minimo is not None:
        anuncios = [
            anuncio
            for anuncio in anuncios
            if preco_decimal(anuncio["preco"]) >= preco_minimo
        ]
    if preco_maximo is not None:
        anuncios = [
            anuncio
            for anuncio in anuncios
            if preco_decimal(anuncio["preco"]) <= preco_maximo
        ]

    if ordem == "mais_vistos":
        anuncios.sort(
            key=lambda anuncio: (
                anuncio["visualizacoes"] or 0,
                anuncio["criado_em"],
                anuncio["id"],
            ),
            reverse=True,
        )
    elif ordem == "menor_preco":
        anuncios.sort(
            key=lambda anuncio: (preco_decimal(anuncio["preco"]), anuncio["id"])
        )
    elif ordem == "maior_preco":
        anuncios.sort(
            key=lambda anuncio: (preco_decimal(anuncio["preco"]), anuncio["id"]),
            reverse=True,
        )

    categorias_loja = sorted(
        {categoria_label(anuncio["categoria"]) for anuncio in anuncios_ativos}
    )
    total_visualizacoes = sum(
        anuncio["visualizacoes"] or 0 for anuncio in anuncios_ativos
    )
    filtros_ativos = bool(
        busca
        or categoria
        or preco_minimo_texto
        or preco_maximo_texto
        or ordem != "recentes"
    )
    reputacao = calcular_reputacao_usuario(db, loja)["vendedor"]
    palavras_nome = [palavra for palavra in nome_publico.split() if palavra]
    logo_iniciais = "".join(palavra[0] for palavra in palavras_nome[:2]).upper()
    descricao_seo = re.sub(r"\s+", " ", loja["loja_descricao"] or "").strip()
    if not descricao_seo:
        descricao_seo = (
            f"Conheça a loja {nome_publico} e seus anúncios no Mercado Colatina."
        )
    descricao_seo = descricao_seo[:155]

    whatsapp_url = None
    numero_comercial = limpar_whatsapp(loja["loja_whatsapp"] or "")
    if len(numero_comercial) in {10, 11, 12, 13}:
        if not numero_comercial.startswith("55"):
            numero_comercial = f"55{numero_comercial}"
        mensagem = quote(f"Olá! Conheci a loja {nome_publico} no Mercado Colatina.")
        whatsapp_url = f"https://wa.me/{numero_comercial}?text={mensagem}"

    loja_url = url_loja_publica(loja, externa=True)
    opcoes_imagem = {"_external": True}
    if FLASK_ENV == "production":
        opcoes_imagem["_scheme"] = "https"
    imagem_social = url_for(
        "static", filename="mercado-colatina-social.svg", **opcoes_imagem
    )
    return render_template(
        "loja_publica.html",
        loja=loja,
        nome_publico=nome_publico,
        logo_iniciais=logo_iniciais or "MC",
        anuncios=anuncios,
        total_anuncios=len(anuncios_ativos),
        total_resultados=len(anuncios),
        total_visualizacoes=total_visualizacoes,
        categorias_loja=categorias_loja,
        busca_loja=busca,
        categoria_selecionada=categoria,
        preco_minimo=preco_minimo_texto,
        preco_maximo=preco_maximo_texto,
        ordem=ordem,
        filtros_ativos=filtros_ativos,
        reputacao_publica=reputacao,
        produtos_vendidos=reputacao["vendas_concluidas"],
        whatsapp_url=whatsapp_url,
        loja_url=loja_url,
        descricao_seo=descricao_seo,
        imagem_social=imagem_social,
    )


@app.route("/anuncio/<int:anuncio_id>")
def anuncio(anuncio_id):
    db = get_db()
    anuncio_item = db.execute(
        "SELECT a.*, u.nome AS vendedor_nome, u.loja_nome, u.whatsapp, "
        "u.criado_em AS vendedor_criado_em, "
        "u.ultimo_acesso_em, u.loja_verificada "
        "FROM anuncios a "
        "JOIN usuarios u ON a.usuario_id = u.id "
        "WHERE a.id=? AND a.ativo=1 AND a.estoque>0",
        (anuncio_id,),
    ).fetchone()
    if not anuncio_item:
        flash("Anúncio não encontrado.", "erro")
        return redirect(url_for("index"))

    if not pode_administrar_loja(anuncio_item["usuario_id"]):
        db.execute(
            "UPDATE anuncios SET visualizacoes = visualizacoes + 1 WHERE id=?",
            (anuncio_id,),
        )
        db.commit()
    fotos = db.execute(
        "SELECT * FROM anuncio_fotos WHERE anuncio_id=? ORDER BY ordem, id",
        (anuncio_id,),
    ).fetchall()
    vendedor_reputacao = calcular_reputacao_usuario(
        db,
        {
            "id": anuncio_item["usuario_id"],
            "criado_em": anuncio_item["vendedor_criado_em"],
            "ultimo_acesso_em": anuncio_item["ultimo_acesso_em"],
            "loja_verificada": anuncio_item["loja_verificada"],
        },
    )["vendedor"]
    vendedor_loja_url = url_loja_publica(
        {
            "id": anuncio_item["usuario_id"],
            "nome": anuncio_item["vendedor_nome"],
            "loja_nome": anuncio_item["loja_nome"],
        }
    )
    produto_url = url_publica("anuncio", anuncio_id=anuncio_id)
    if anuncio_item["foto"]:
        if anuncio_item["foto"].startswith(("http://", "https://")):
            produto_imagem = foto_url(anuncio_item["foto"], 1200)
        else:
            produto_imagem = url_publica("uploaded_file", filename=anuncio_item["foto"])
    else:
        produto_imagem = url_publica("static", filename="mercado-colatina-social.svg")
    return render_template(
        "anuncio.html",
        a=anuncio_item,
        fotos=fotos,
        vendedor_reputacao=vendedor_reputacao,
        vendedor_loja_url=vendedor_loja_url,
        denuncia_motivos=DENUNCIA_MOTIVOS,
        produto_url=produto_url,
        produto_imagem=produto_imagem,
    )


@app.route("/anuncio/<int:anuncio_id>/contato")
def contato_anuncio(anuncio_id):
    db = get_db()
    anuncio_item = db.execute(
        "SELECT a.id, a.titulo, a.usuario_id, u.whatsapp FROM anuncios a "
        "JOIN usuarios u ON u.id=a.usuario_id WHERE a.id=? AND a.ativo=1 AND a.estoque>0 AND u.ativo=1",
        (anuncio_id,),
    ).fetchone()
    if not anuncio_item:
        abort(404)
    if not pode_administrar_loja(anuncio_item["usuario_id"]):
        db.execute(
            "UPDATE anuncios SET contatos_whatsapp=contatos_whatsapp+1 WHERE id=?",
            (anuncio_id,),
        )
        db.commit()
    numero = limpar_whatsapp(anuncio_item["whatsapp"])
    if not numero.startswith("55"):
        numero = f"55{numero}"
    mensagem = quote(
        f"Olá! Vi seu anúncio {anuncio_item['titulo']} no Mercado Colatina. Ainda está disponível?"
    )
    return redirect(f"https://wa.me/{numero}?text={mensagem}")


@app.route("/anuncio/<int:anuncio_id>/denunciar", methods=["POST"])
def denunciar_anuncio(anuncio_id):
    if not logado():
        flash("Entre na sua conta para denunciar um anúncio.", "erro")
        return redirect(url_for("login"))

    db = get_db()
    anuncio_item = db.execute(
        "SELECT id, usuario_id FROM anuncios WHERE id=? AND ativo=1",
        (anuncio_id,),
    ).fetchone()
    if not anuncio_item:
        abort(404)
    if pode_administrar_loja(anuncio_item["usuario_id"]):
        flash("Você não pode denunciar o próprio anúncio.", "erro")
        return redirect(url_for("anuncio", anuncio_id=anuncio_id))

    motivo = request.form.get("motivo", "")
    detalhes = request.form.get("detalhes", "").strip()
    if motivo not in DENUNCIA_MOTIVOS:
        flash("Selecione um motivo valido para a denuncia.", "erro")
        return redirect(url_for("anuncio", anuncio_id=anuncio_id))
    if len(detalhes) > 500:
        flash("Os detalhes devem ter no maximo 500 caracteres.", "erro")
        return redirect(url_for("anuncio", anuncio_id=anuncio_id))

    existente = db.execute(
        "SELECT id FROM denuncias WHERE anuncio_id=? AND denunciante_id=? AND status='pendente'",
        (anuncio_id, session["usuario_id"]),
    ).fetchone()
    if existente:
        flash("Sua denuncia deste anuncio ja esta em analise.", "erro")
        return redirect(url_for("anuncio", anuncio_id=anuncio_id))

    db.execute(
        "INSERT INTO denuncias (anuncio_id, denunciante_id, motivo, detalhes) VALUES (?,?,?,?)",
        (anuncio_id, session["usuario_id"], motivo, detalhes),
    )
    db.commit()
    flash("Denuncia recebida. Nossa equipe fara a analise.", "ok")
    return redirect(url_for("anuncio", anuncio_id=anuncio_id))


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if logado():
        return redirect(url_for("index"))
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        username = request.form.get("username", "").strip()
        senha = request.form.get("senha", "").strip()
        whatsapp = limpar_whatsapp(request.form.get("whatsapp", "").strip())
        erro = validar_usuario(nome, username, senha, whatsapp)
        if erro:
            flash(erro, "erro")
            return render_template("cadastro.html")
        if request.form.get("aceite_termos") != "1":
            flash(
                "Para criar a conta, aceite os Termos de Uso e a Politica de Privacidade.",
                "erro",
            )
            return render_template("cadastro.html")
        db = get_db()
        try:
            fundador, fundador_origem = reservar_selo_fundador(db)
            db.execute(
                "INSERT INTO usuarios (nome, username, senha, whatsapp, "
                "termos_aceitos_em, fundador, fundador_desde, fundador_origem) "
                "VALUES (?,?,?,?,CURRENT_TIMESTAMP,?,CASE WHEN ?=1 THEN "
                "CURRENT_TIMESTAMP ELSE NULL END,?)",
                (
                    nome,
                    username,
                    generate_password_hash(senha),
                    whatsapp,
                    fundador,
                    fundador,
                    fundador_origem,
                ),
            )
            db.commit()
            mensagem = "Conta criada! Faça login."
            if fundador:
                mensagem += " Você agora é Fundador do Mercado Colatina!"
            flash(mensagem, "ok")
            return redirect(url_for("login"))
        except Exception:
            db.rollback()
            flash("Username ja em uso. Escolha outro.", "erro")
    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if logado():
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"].strip()
        senha = request.form["senha"].strip()
        if not username or not senha:
            flash("Preencha usuário e senha.", "erro")
            return render_template("login.html")
        db = get_db()
        chave_login = chave_tentativa_login(username)
        if login_temporariamente_bloqueado(db, chave_login):
            flash(
                "Muitas tentativas seguidas. Aguarde 15 minutos e tente novamente.",
                "erro",
            )
            return render_template("login.html"), 429
        usuario = db.execute(
            "SELECT * FROM usuarios WHERE username=? AND ativo=1",
            (username,),
        ).fetchone()
        if usuario and check_password_hash(usuario["senha"], senha):
            db.execute("DELETE FROM tentativas_login WHERE chave=?", (chave_login,))
            db.execute(
                "UPDATE usuarios SET ultimo_acesso_em=CURRENT_TIMESTAMP WHERE id=?",
                (usuario["id"],),
            )
            db.commit()
            visita_registrada = session.get("_visita_registrada")
            session.clear()
            if visita_registrada:
                session["_visita_registrada"] = True
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            session["usuario_username"] = usuario["username"]
            session["is_admin"] = bool(usuario["is_admin"])
            session["loja_ativa_id"] = usuario["id"]
            flash(f"Bem-vindo, {usuario['nome']}!", "ok")
            if len(listar_lojas_administradas(usuario["id"])) > 1:
                return redirect(url_for("minhas_lojas"))
            return redirect(url_for("index"))
        registrar_falha_login(db, chave_login)
        flash("Usuário ou senha incorretos.", "erro")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    visita_registrada = session.get("_visita_registrada")
    session.clear()
    if visita_registrada:
        session["_visita_registrada"] = True
    return redirect(url_for("index"))


@app.route("/minhas-lojas")
def minhas_lojas():
    if not logado():
        return redirect(url_for("login"))
    lojas = listar_lojas_administradas()
    return render_template(
        "minhas_lojas.html", lojas=lojas, loja_ativa_id=loja_ativa_id()
    )


@app.route("/minhas-lojas/<int:loja_id>/selecionar", methods=["POST"])
def selecionar_loja(loja_id):
    if not logado():
        return redirect(url_for("login"))
    lojas = listar_lojas_administradas()
    loja = next((item for item in lojas if item["id"] == loja_id), None)
    if not loja:
        abort(403)
    session["loja_ativa_id"] = loja_id
    flash(f"Agora voce esta administrando {nome_loja_publica(loja)}.", "ok")
    destino = request.form.get("destino", "painel_vendedor")
    if destino not in {"painel_vendedor", "meus_anuncios", "criar_anuncio"}:
        destino = "painel_vendedor"
    return redirect(url_for(destino))


@app.route("/minha-conta", methods=["GET", "POST"])
def minha_conta():
    if not logado():
        return redirect(url_for("login"))

    db = get_db()
    usuario = db.execute(
        "SELECT * FROM usuarios WHERE id=?",
        (session["usuario_id"],),
    ).fetchone()

    if request.method == "POST":
        acao = request.form.get("acao", "senha")
        if acao == "perfil":
            nome = request.form.get("nome", "").strip()
            whatsapp = limpar_whatsapp(request.form.get("whatsapp", ""))
            if len(nome) < 3 or len(nome) > 80:
                flash("Informe um nome com 3 a 80 caracteres.", "erro")
            elif len(whatsapp) not in {10, 11}:
                flash("WhatsApp invalido. Informe DDD + numero.", "erro")
            else:
                db.execute(
                    "UPDATE usuarios SET nome=?, whatsapp=? WHERE id=?",
                    (nome, whatsapp, session["usuario_id"]),
                )
                db.commit()
                session["usuario_nome"] = nome
                flash("Dados pessoais atualizados.", "ok")
        else:
            atual = request.form.get("senha_atual", "").strip()
            nova = request.form.get("nova_senha", "").strip()
            confirma = request.form.get("confirmar", "").strip()

            if not check_password_hash(usuario["senha"], atual):
                flash("Senha atual incorreta.", "erro")
            elif nova != confirma:
                flash("Nova senha e confirmação não coincidem.", "erro")
            elif len(nova) < 8:
                flash("Use uma senha com pelo menos 8 caracteres.", "erro")
            else:
                db.execute(
                    "UPDATE usuarios SET senha=? WHERE id=?",
                    (generate_password_hash(nova), session["usuario_id"]),
                )
                db.commit()
                flash("Senha alterada com sucesso!", "ok")

        usuario = db.execute(
            "SELECT * FROM usuarios WHERE id=?",
            (session["usuario_id"],),
        ).fetchone()

    reputacao = calcular_reputacao_usuario(db, usuario)
    return render_template(
        "minha_conta.html",
        usuario=usuario,
        reputacao_vendedor=reputacao["vendedor"],
        reputacao_comprador=reputacao["comprador"],
    )


@app.route("/recuperar-acesso", methods=["GET", "POST"])
def recuperar_acesso():
    if logado():
        return redirect(url_for("minha_conta"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if not USERNAME_RE.fullmatch(username):
            flash("Informe o nome de usuario usado no cadastro.", "erro")
            return render_template("recuperar_acesso.html")
        numero = limpar_whatsapp(SUPPORT_WHATSAPP)
        if not numero.startswith("55"):
            numero = f"55{numero}"
        mensagem = (
            "Olá! Preciso recuperar meu acesso ao Mercado Colatina. "
            f"Meu nome de usuário é @{username}."
        )
        return redirect(f"https://wa.me/{numero}?text={quote(mensagem)}")
    return render_template("recuperar_acesso.html")


@app.route("/minha-conta/desativar", methods=["POST"])
def desativar_conta():
    if not logado():
        return redirect(url_for("login"))
    db = get_db()
    usuario = db.execute(
        "SELECT senha FROM usuarios WHERE id=?", (session["usuario_id"],)
    ).fetchone()
    senha = request.form.get("senha", "")
    if not usuario or not check_password_hash(usuario["senha"], senha):
        flash("Senha incorreta. A conta não foi desativada.", "erro")
        return redirect(url_for("minha_conta"))
    pedido_aberto = db.execute(
        "SELECT id FROM pedidos WHERE (comprador_id=? OR vendedor_id=?) "
        "AND status IN ('aguardando','confirmado','em_analise') LIMIT 1",
        (session["usuario_id"], session["usuario_id"]),
    ).fetchone()
    if pedido_aberto:
        flash(
            "Conclua ou cancele seus pedidos em andamento antes de desativar a conta.",
            "erro",
        )
        return redirect(url_for("minha_conta"))

    usuario_id = session["usuario_id"]
    db.execute("UPDATE anuncios SET ativo=0 WHERE usuario_id=?", (usuario_id,))
    db.execute(
        "UPDATE usuarios SET ativo=0, mp_access_token=NULL, mp_refresh_token=NULL, "
        "mp_user_id=NULL, mp_token_expira=NULL, mp_conectado_em=NULL WHERE id=?",
        (usuario_id,),
    )
    db.commit()
    session.clear()
    flash("Sua conta foi desativada e os anuncios foram ocultados.", "ok")
    return redirect(url_for("index"))


@app.route("/mercadopago/conectar")
def mercadopago_conectar():
    if not logado():
        return redirect(url_for("login"))
    if not mercadopago_configurado():
        flash("A integracao com o Mercado Pago ainda esta sendo configurada.", "erro")
        return redirect(url_for("minha_conta"))

    state = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode("ascii")).digest())
        .rstrip(b"=")
        .decode("ascii")
    )
    session["mp_oauth_state"] = state
    session["mp_code_verifier"] = code_verifier
    return redirect(criar_url_autorizacao(state, code_challenge))


@app.route("/mercadopago/oauth/callback")
def mercadopago_oauth_callback():
    if not logado():
        return redirect(url_for("login"))
    state = request.args.get("state", "")
    code = request.args.get("code", "")
    state_sessao = session.pop("mp_oauth_state", None)
    code_verifier = session.pop("mp_code_verifier", None)
    if not state or not state_sessao or not secrets.compare_digest(state, state_sessao):
        flash("Nao foi possivel validar a conexao com o Mercado Pago.", "erro")
        return redirect(url_for("minha_conta"))
    if not code or not code_verifier:
        flash("Autorizacao do Mercado Pago cancelada ou expirada.", "erro")
        return redirect(url_for("minha_conta"))
    try:
        dados = trocar_codigo_por_token(code, code_verifier)
        salvar_tokens_mercadopago(get_db(), session["usuario_id"], dados)
    except MercadoPagoError:
        app.logger.exception("Falha ao conectar conta Mercado Pago")
        flash("Nao foi possivel conectar o Mercado Pago. Tente novamente.", "erro")
        return redirect(url_for("minha_conta"))
    flash("Conta Mercado Pago conectada com sucesso!", "ok")
    return redirect(url_for("minha_conta"))


@app.route("/mercadopago/desconectar", methods=["POST"])
def mercadopago_desconectar():
    if not logado():
        return redirect(url_for("login"))
    db = get_db()
    pedido_aberto = db.execute(
        "SELECT id FROM pedidos WHERE vendedor_id=? AND status IN ('confirmado','em_analise') "
        "AND pagamento_status IN ('aguardando','pendente','aprovado') LIMIT 1",
        (session["usuario_id"],),
    ).fetchone()
    if pedido_aberto:
        flash("Conclua os pedidos pagos ou em andamento antes de desconectar.", "erro")
        return redirect(url_for("minha_conta"))
    db.execute(
        "UPDATE usuarios SET mp_access_token=NULL, mp_refresh_token=NULL, mp_user_id=NULL, "
        "mp_token_expira=NULL, mp_conectado_em=NULL WHERE id=?",
        (session["usuario_id"],),
    )
    db.commit()
    flash("Conta Mercado Pago desconectada.", "ok")
    return redirect(url_for("minha_conta"))


@app.route("/criar", methods=["GET", "POST"])
def criar_anuncio():
    if not logado():
        flash("Faça login para anunciar.", "erro")
        return redirect(url_for("login"))

    vendedor_id = loja_ativa_id()
    pode, aviso = pode_criar_anuncio(vendedor_id)
    if not pode:
        return redirect(url_for("assinar"))
    rascunho_neo = session.pop("_neo_rascunho", {})

    if request.method == "POST":
        pode, _ = pode_criar_anuncio(vendedor_id)
        if not pode:
            return redirect(url_for("assinar"))

        titulo = request.form["titulo"].strip()
        descricao = request.form["descricao"].strip()
        preco = normalizar_preco(request.form["preco"])
        categoria = request.form["categoria"]
        condicao = request.form["condicao"]
        bairro = request.form.get("bairro", "").strip()
        estoque, erro_estoque = validar_estoque(request.form.get("estoque", "1"))
        if erro_estoque:
            flash(erro_estoque, "erro")
            return render_template("criar.html", categorias=CATEGORIAS, aviso=aviso)
        erro = validar_anuncio(titulo, descricao, preco, categoria, condicao, bairro)
        if erro:
            flash(erro, "erro")
            return render_template("criar.html", categorias=CATEGORIAS, aviso=aviso)
        arquivos = [
            arquivo for arquivo in request.files.getlist("fotos") if arquivo.filename
        ]
        if len(arquivos) > 5:
            flash("Envie no máximo cinco fotos por anúncio.", "erro")
            return render_template("criar.html", categorias=CATEGORIAS, aviso=aviso)
        for arquivo in arquivos:
            if not allowed_file(arquivo.filename):
                flash("Formato de imagem inválido. Use JPG, JPEG, PNG ou WEBP.", "erro")
                return render_template("criar.html", categorias=CATEGORIAS, aviso=aviso)
            extensao = arquivo.filename.rsplit(".", 1)[1].lower()
            if not arquivo_e_imagem_valida(arquivo, extensao):
                flash("Um dos arquivos enviados não é uma imagem válida.", "erro")
                return render_template("criar.html", categorias=CATEGORIAS, aviso=aviso)

        fotos_salvas = []
        try:
            for arquivo in arquivos:
                extensao = arquivo.filename.rsplit(".", 1)[1].lower()
                fotos_salvas.append(
                    salvar_imagem(
                        arquivo,
                        extensao,
                        app.config["UPLOAD_FOLDER"],
                        permitir_externo=not app.testing,
                    )
                )
        except Exception:
            app.logger.exception("Falha ao armazenar imagens do anúncio")
            for foto_salva, foto_id_salva in fotos_salvas:
                excluir_imagem(
                    foto_salva,
                    foto_id_salva,
                    app.config["UPLOAD_FOLDER"],
                    permitir_externo=not app.testing,
                )
            flash("Não foi possível enviar as imagens. Tente novamente.", "erro")
            return render_template("criar.html", categorias=CATEGORIAS, aviso=aviso)

        foto, foto_id = fotos_salvas[0] if fotos_salvas else (None, None)

        db = get_db()
        anuncio_id = db.execute(
            "INSERT INTO anuncios (usuario_id, titulo, descricao, preco, categoria, condicao, bairro, estoque, foto, foto_id) "
            "VALUES (?,?,?,?,?,?,?,?,?,?) RETURNING id",
            (
                vendedor_id,
                titulo,
                descricao,
                preco,
                categoria,
                condicao,
                bairro,
                estoque,
                foto,
                foto_id,
            ),
        ).fetchone()[0]
        for ordem, (foto_salva, foto_id_salva) in enumerate(fotos_salvas):
            db.execute(
                "INSERT INTO anuncio_fotos (anuncio_id, foto, foto_id, ordem) VALUES (?,?,?,?)",
                (anuncio_id, foto_salva, foto_id_salva, ordem),
            )
        db.commit()
        flash("Anúncio publicado!", "ok")
        return redirect(url_for("meus_anuncios"))

    return render_template(
        "criar.html", categorias=CATEGORIAS, aviso=aviso, rascunho_neo=rascunho_neo
    )


@app.route("/neo/anuncio", methods=["POST"])
def neo_criar_rascunho():
    if not logado():
        return redirect(url_for("login"))
    if not neo_configurado():
        flash("O Neo ainda está em configuração.", "erro")
        return redirect(url_for("criar_anuncio"))
    agora = int(time.time())
    if agora - int(session.get("_neo_ultimo", 0)) < 30:
        flash("Aguarde alguns segundos antes de pedir outro rascunho ao Neo.", "erro")
        return redirect(url_for("criar_anuncio"))
    relato = request.form.get("relato", "").strip()
    if len(relato) < 10 or len(relato) > 800:
        flash(
            "Conte ao Neo o que deseja vender usando entre 10 e 800 caracteres.", "erro"
        )
        return redirect(url_for("criar_anuncio"))
    session["_neo_ultimo"] = agora
    try:
        rascunho = gerar_rascunho(relato)
    except Exception:
        app.logger.exception("Falha ao gerar rascunho com o Neo")
        flash(
            "O Neo não conseguiu criar o rascunho agora. Preencha o anúncio manualmente.",
            "erro",
        )
        return redirect(url_for("criar_anuncio"))
    if rascunho.pop("requer_revisao", False):
        flash(
            rascunho.pop("alerta", "Este item precisa de revisão antes da publicação."),
            "erro",
        )
        return redirect(url_for("criar_anuncio"))
    rascunho.pop("alerta", None)
    session["_neo_rascunho"] = rascunho
    flash(
        "O Neo preparou um rascunho. Revise todas as informações antes de publicar.",
        "ok",
    )
    return redirect(url_for("criar_anuncio"))


@app.route("/editar/<int:anuncio_id>", methods=["GET", "POST"])
def editar_anuncio(anuncio_id):
    if not logado():
        return redirect(url_for("login"))

    db = get_db()
    anuncio_item = db.execute(
        "SELECT * FROM anuncios WHERE id=? AND excluido_em IS NULL",
        (anuncio_id,),
    ).fetchone()
    if not anuncio_item or not pode_administrar_loja(anuncio_item["usuario_id"]):
        abort(404)
    fotos_atuais = db.execute(
        "SELECT * FROM anuncio_fotos WHERE anuncio_id=? ORDER BY ordem, id",
        (anuncio_id,),
    ).fetchall()

    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        descricao = request.form["descricao"].strip()
        preco = normalizar_preco(request.form["preco"])
        categoria = request.form["categoria"]
        condicao = request.form["condicao"]
        bairro = request.form.get("bairro", "").strip()
        estoque, erro_estoque = validar_estoque(
            request.form.get("estoque", anuncio_item["estoque"]), minimo=0
        )
        if erro_estoque:
            flash(erro_estoque, "erro")
            return render_template(
                "editar.html", a=anuncio_item, fotos=fotos_atuais, categorias=CATEGORIAS
            )
        erro = validar_anuncio(titulo, descricao, preco, categoria, condicao, bairro)
        if erro:
            flash(erro, "erro")
            return render_template(
                "editar.html", a=anuncio_item, fotos=fotos_atuais, categorias=CATEGORIAS
            )

        foto = anuncio_item["foto"]
        foto_id = anuncio_item["foto_id"]
        arquivos = [
            arquivo for arquivo in request.files.getlist("fotos") if arquivo.filename
        ]
        if len(arquivos) > 5:
            flash("Envie no máximo cinco fotos por anúncio.", "erro")
            return render_template(
                "editar.html", a=anuncio_item, fotos=fotos_atuais, categorias=CATEGORIAS
            )
        for arquivo in arquivos:
            if not allowed_file(arquivo.filename):
                flash("Formato de imagem inválido. Use JPG, JPEG, PNG ou WEBP.", "erro")
                return render_template(
                    "editar.html",
                    a=anuncio_item,
                    fotos=fotos_atuais,
                    categorias=CATEGORIAS,
                )
            extensao = arquivo.filename.rsplit(".", 1)[1].lower()
            if not arquivo_e_imagem_valida(arquivo, extensao):
                flash("Um dos arquivos enviados não é uma imagem válida.", "erro")
                return render_template(
                    "editar.html",
                    a=anuncio_item,
                    fotos=fotos_atuais,
                    categorias=CATEGORIAS,
                )

        novas_fotos = []
        if arquivos:
            try:
                for arquivo in arquivos:
                    extensao = arquivo.filename.rsplit(".", 1)[1].lower()
                    novas_fotos.append(
                        salvar_imagem(
                            arquivo,
                            extensao,
                            app.config["UPLOAD_FOLDER"],
                            permitir_externo=not app.testing,
                        )
                    )
            except Exception:
                app.logger.exception("Falha ao substituir imagens do anúncio")
                for foto_nova, foto_id_nova in novas_fotos:
                    excluir_imagem(
                        foto_nova,
                        foto_id_nova,
                        app.config["UPLOAD_FOLDER"],
                        permitir_externo=not app.testing,
                    )
                flash(
                    "Não foi possível enviar as novas imagens. Tente novamente.", "erro"
                )
                return render_template(
                    "editar.html",
                    a=anuncio_item,
                    fotos=fotos_atuais,
                    categorias=CATEGORIAS,
                )
            foto, foto_id = novas_fotos[0]

        db.execute(
            "UPDATE anuncios SET titulo=?, descricao=?, preco=?, categoria=?, condicao=?, bairro=?, estoque=?, ativo=CASE WHEN ?=0 THEN 0 ELSE ativo END, foto=?, foto_id=? WHERE id=?",
            (
                titulo,
                descricao,
                preco,
                categoria,
                condicao,
                bairro,
                estoque,
                estoque,
                foto,
                foto_id,
                anuncio_id,
            ),
        )
        if novas_fotos:
            db.execute("DELETE FROM anuncio_fotos WHERE anuncio_id=?", (anuncio_id,))
            for ordem, (foto_nova, foto_id_nova) in enumerate(novas_fotos):
                db.execute(
                    "INSERT INTO anuncio_fotos (anuncio_id, foto, foto_id, ordem) VALUES (?,?,?,?)",
                    (anuncio_id, foto_nova, foto_id_nova, ordem),
                )
        db.commit()

        if novas_fotos:
            for foto_antiga in fotos_atuais:
                try:
                    excluir_imagem(
                        foto_antiga["foto"],
                        foto_antiga["foto_id"],
                        app.config["UPLOAD_FOLDER"],
                        permitir_externo=not app.testing,
                    )
                except Exception:
                    app.logger.exception("Falha ao remover imagem antiga do anúncio")

        flash("Anúncio atualizado com sucesso.", "ok")
        return redirect(url_for("meus_anuncios"))

    return render_template(
        "editar.html", a=anuncio_item, fotos=fotos_atuais, categorias=CATEGORIAS
    )


@app.route("/meus-anuncios/<int:anuncio_id>/status", methods=["POST"])
def alternar_status_anuncio(anuncio_id):
    if not logado():
        return redirect(url_for("login"))
    db = get_db()
    anuncio_item = db.execute(
        "SELECT usuario_id, ativo, estoque FROM anuncios "
        "WHERE id=? AND excluido_em IS NULL",
        (anuncio_id,),
    ).fetchone()
    if not anuncio_item or not pode_administrar_loja(anuncio_item["usuario_id"]):
        abort(404)
    novo_status = 0 if anuncio_item["ativo"] else 1
    if novo_status:
        if anuncio_item["estoque"] <= 0:
            flash(
                "Informe uma quantidade em estoque antes de reativar o anuncio.", "erro"
            )
            return redirect(url_for("meus_anuncios"))
        pode, _ = pode_criar_anuncio(anuncio_item["usuario_id"])
        if not pode:
            flash("Seu limite de anúncios ativos foi atingido.", "erro")
            return redirect(url_for("assinar"))
    db.execute("UPDATE anuncios SET ativo=? WHERE id=?", (novo_status, anuncio_id))
    db.commit()
    flash("Anúncio reativado." if novo_status else "Anúncio pausado.", "ok")
    return redirect(url_for("meus_anuncios"))


@app.route("/assinar")
def assinar():
    if not logado():
        return redirect(url_for("login"))
    db = get_db()
    usuario = db.execute(
        "SELECT plano_ativo, plano_expira FROM usuarios WHERE id=?",
        (session["usuario_id"],),
    ).fetchone()
    pagamento = db.execute(
        "SELECT * FROM pagamentos WHERE usuario_id=? ORDER BY criado_em DESC LIMIT 1",
        (session["usuario_id"],),
    ).fetchone()
    return render_template(
        "assinar.html",
        valor=VALOR_PLANO,
        pix=PIX_CHAVE,
        titular=PIX_TITULAR,
        pagamento=pagamento,
        plano_ativo=plano_valido(usuario),
        plano_expira=usuario["plano_expira"],
    )


@app.route("/pagamento/pix/solicitar", methods=["POST"])
def solicitar_pagamento_pix():
    if not logado():
        return redirect(url_for("login"))
    db = get_db()
    pagamento = db.execute(
        "SELECT * FROM pagamentos WHERE usuario_id=? AND status='pendente' ORDER BY criado_em DESC LIMIT 1",
        (session["usuario_id"],),
    ).fetchone()
    if not pagamento:
        referencia = f"MC-{session['usuario_id']}-{secrets.token_hex(4).upper()}"
        db.execute(
            "INSERT INTO pagamentos (usuario_id, valor, metodo, status, referencia) VALUES (?,?,?,?,?)",
            (session["usuario_id"], VALOR_PLANO_BANCO, "PIX", "pendente", referencia),
        )
        db.commit()
        pagamento = db.execute(
            "SELECT * FROM pagamentos WHERE referencia=?",
            (referencia,),
        ).fetchone()

    numero = limpar_whatsapp(PAGAMENTO_WHATSAPP)
    if not numero.startswith("55"):
        numero = f"55{numero}"
    mensagem = (
        f"Olá! Fiz o PIX de {VALOR_PLANO} para o Mercado Colatina. "
        f"Usuário: @{session['usuario_username']}. Referência: {pagamento['referencia']}. "
        "Vou enviar o comprovante nesta conversa."
    )
    return redirect(f"https://wa.me/{numero}?text={quote(mensagem)}")


@app.route("/meus-anuncios")
def meus_anuncios():
    if not logado():
        return redirect(url_for("login"))
    db = get_db()
    vendedor_id = loja_ativa_id()
    anuncios = db.execute(
        "SELECT * FROM anuncios WHERE usuario_id=? AND excluido_em IS NULL "
        "ORDER BY criado_em DESC",
        (vendedor_id,),
    ).fetchall()
    vendedor = db.execute(
        "SELECT id, nome, loja_nome FROM usuarios WHERE id=? AND ativo=1",
        (vendedor_id,),
    ).fetchone()
    return render_template("meus_anuncios.html", anuncios=anuncios, vendedor=vendedor)


@app.route("/painel-vendedor")
def painel_vendedor():
    if not logado():
        return redirect(url_for("login"))

    db = get_db()
    usuario_id = loja_ativa_id()
    vendedor = db.execute(
        "SELECT id, nome, whatsapp, loja_nome, loja_descricao, loja_bairro, "
        "loja_whatsapp, criado_em, ultimo_acesso_em, loja_verificada, "
        "fundador, fundador_desde "
        "FROM usuarios WHERE id=? AND ativo=1",
        (usuario_id,),
    ).fetchone()
    if not vendedor:
        abort(403)

    anuncios = list(
        db.execute(
            "SELECT * FROM anuncios WHERE usuario_id=? AND excluido_em IS NULL "
            "ORDER BY criado_em DESC, id DESC",
            (usuario_id,),
        ).fetchall()
    )
    pedidos_vendedor = list(
        db.execute(
            "SELECT p.*, a.titulo, a.foto, comprador.nome AS comprador_nome, "
            "COALESCE(conclusao.criado_em, p.atualizado_em) AS concluido_em "
            "FROM pedidos p "
            "JOIN anuncios a ON a.id=p.anuncio_id "
            "JOIN usuarios comprador ON comprador.id=p.comprador_id "
            "LEFT JOIN pedido_eventos conclusao ON conclusao.pedido_id=p.id "
            "AND conclusao.tipo='PEDIDO_CONCLUIDO' "
            "WHERE p.vendedor_id=? ORDER BY p.criado_em DESC, p.id DESC",
            (usuario_id,),
        ).fetchall()
    )

    anuncios_ativos = [a for a in anuncios if a["ativo"] and a["estoque"] > 0]
    anuncios_esgotados = [a for a in anuncios if a["estoque"] <= 0]
    anuncios_pausados = [a for a in anuncios if not a["ativo"] and a["estoque"] > 0]
    estoque_baixo = [a for a in anuncios_ativos if a["estoque"] <= 2]
    vendas_concluidas = [p for p in pedidos_vendedor if p["status"] == "concluido"]
    pedidos_em_analise = [p for p in pedidos_vendedor if p["status"] == "em_analise"]
    pedidos_cancelados = [
        p for p in pedidos_vendedor if p["status"] in {"cancelado", "recusado"}
    ]
    pedidos_aguardando_acao = [
        p
        for p in pedidos_vendedor
        if p["status"] == "aguardando"
        or (p["status"] == "confirmado" and not p["vendedor_confirmou_em"])
    ]

    filtro = request.args.get("filtro", "todos")
    filtros_validos = {
        "todos",
        "ativos",
        "pausados",
        "esgotados",
        "mais_vistos",
        "sem_visualizacoes",
        "recentes",
    }
    if filtro not in filtros_validos:
        filtro = "todos"
    anuncios_filtrados = list(anuncios)
    if filtro == "ativos":
        anuncios_filtrados = anuncios_ativos
    elif filtro == "pausados":
        anuncios_filtrados = anuncios_pausados
    elif filtro == "esgotados":
        anuncios_filtrados = anuncios_esgotados
    elif filtro == "mais_vistos":
        anuncios_filtrados.sort(
            key=lambda anuncio: (anuncio["visualizacoes"], anuncio["id"]), reverse=True
        )
    elif filtro == "sem_visualizacoes":
        anuncios_filtrados = [a for a in anuncios if not a["visualizacoes"]]
    elif filtro == "recentes":
        anuncios_filtrados = anuncios[:6]

    duracoes = []
    for pedido in vendas_concluidas:
        inicio = converter_data_hora(pedido["criado_em"])
        fim = converter_data_hora(pedido["concluido_em"])
        if inicio and fim:
            if inicio.tzinfo is not None and fim.tzinfo is None:
                inicio = inicio.replace(tzinfo=None)
            elif fim.tzinfo is not None and inicio.tzinfo is None:
                fim = fim.replace(tzinfo=None)
            duracoes.append(max(0, (fim - inicio).total_seconds()))

    total_pedidos = len(pedidos_vendedor)
    taxa_conclusao = (
        round(len(vendas_concluidas) * 100 / total_pedidos) if total_pedidos else 0
    )
    tempo_medio = sum(duracoes) / len(duracoes) if duracoes else None
    resumo = {
        "anuncios_ativos": len(anuncios_ativos),
        "anuncios_pausados": len(anuncios_pausados),
        "produtos_esgotados": len(anuncios_esgotados),
        "estoque_baixo": len(estoque_baixo),
        "pedidos_aguardando_acao": len(pedidos_aguardando_acao),
        "pedidos_em_analise": len(pedidos_em_analise),
        "vendas_concluidas": len(vendas_concluidas),
        "itens_vendidos": len(vendas_concluidas),
    }
    estatisticas = {
        "anuncios": len(anuncios),
        "vendas": len(vendas_concluidas),
        "pedidos": total_pedidos,
        "em_analise": len(pedidos_em_analise),
        "taxa_conclusao": taxa_conclusao,
        "tempo_medio": formatar_duracao_media(tempo_medio),
    }
    grupos_pedidos = (
        (
            "aguardando",
            "Aguardando minha confirmação",
            [p for p in pedidos_vendedor if p["status"] == "aguardando"],
        ),
        (
            "comprador",
            "Aguardando comprador",
            [p for p in pedidos_vendedor if p["status"] == "confirmado"],
        ),
        ("analise", "Em análise", pedidos_em_analise),
        ("concluidos", "Concluídos", vendas_concluidas),
        ("cancelados", "Cancelados", pedidos_cancelados),
    )
    total_finalizados_reputacao = len(vendas_concluidas) + len(pedidos_cancelados)
    reputacao = {
        "membro_desde": formatar_data_reputacao(vendedor["criado_em"]),
        "vendas_concluidas": len(vendas_concluidas),
        "pedidos_concluidos": len(vendas_concluidas),
        "pedidos_cancelados": len(pedidos_cancelados),
        "pedidos_em_analise": len(pedidos_em_analise),
        "taxa_conclusao": (
            round(len(vendas_concluidas) * 100 / total_finalizados_reputacao)
            if total_finalizados_reputacao
            else 0
        ),
        "tempo_medio_conclusao": formatar_duracao_media(tempo_medio),
        "ultimo_acesso": formatar_data_reputacao(
            vendedor["ultimo_acesso_em"], incluir_hora=True
        ),
        "loja_verificada": bool(vendedor["loja_verificada"]),
    }
    return render_template(
        "painel_vendedor.html",
        vendedor=vendedor,
        resumo=resumo,
        estatisticas=estatisticas,
        reputacao=reputacao,
        anuncios=anuncios_filtrados,
        filtro=filtro,
        grupos_pedidos=grupos_pedidos,
    )


@app.route("/painel-vendedor/perfil", methods=["POST"])
def atualizar_perfil_loja():
    if not logado():
        return redirect(url_for("login"))

    nome = re.sub(r"\s+", " ", request.form.get("loja_nome", "").strip())
    descricao = re.sub(r"\s+", " ", request.form.get("loja_descricao", "").strip())
    bairro = re.sub(r"\s+", " ", request.form.get("loja_bairro", "").strip())
    whatsapp = limpar_whatsapp(request.form.get("loja_whatsapp", ""))
    erro = validar_perfil_loja(nome, descricao, bairro, whatsapp)
    if erro:
        flash(erro, "erro")
        return redirect(url_for("painel_vendedor"))

    db = get_db()
    usuario_id = loja_ativa_id()
    if nome:
        nome_em_uso = db.execute(
            "SELECT id FROM usuarios WHERE lower(loja_nome)=lower(?) AND id<>? LIMIT 1",
            (nome, usuario_id),
        ).fetchone()
        if nome_em_uso:
            flash("Este nome de loja já está em uso. Escolha outro.", "erro")
            return redirect(url_for("painel_vendedor"))

    try:
        db.execute(
            "UPDATE usuarios SET loja_nome=?, loja_descricao=?, loja_bairro=?, "
            "loja_whatsapp=? WHERE id=? AND ativo=1",
            (nome or None, descricao, bairro, whatsapp, usuario_id),
        )
        db.commit()
    except Exception:
        db.rollback()
        app.logger.exception("Falha ao atualizar perfil da loja")
        flash("Não foi possível salvar o perfil da loja. Tente outro nome.", "erro")
        return redirect(url_for("painel_vendedor"))

    flash("Perfil da loja atualizado.", "ok")
    return redirect(url_for("painel_vendedor"))


@app.route("/comprar/<int:anuncio_id>", methods=["GET", "POST"])
def comprar(anuncio_id):
    if not logado():
        flash("Entre na sua conta para fazer um pedido.", "erro")
        return redirect(url_for("login"))

    db = get_db()
    anuncio_item = db.execute(
        "SELECT a.*, u.nome AS vendedor_nome, u.whatsapp "
        "FROM anuncios a JOIN usuarios u ON a.usuario_id=u.id "
        "WHERE a.id=? AND a.ativo=1 AND a.estoque>0",
        (anuncio_id,),
    ).fetchone()
    if not anuncio_item:
        flash("Este anúncio não está mais disponível.", "erro")
        return redirect(url_for("index"))
    if pode_administrar_loja(anuncio_item["usuario_id"]):
        flash("Você não pode comprar o próprio anúncio.", "erro")
        return redirect(url_for("anuncio", anuncio_id=anuncio_id))

    pedido_existente = db.execute(
        "SELECT id FROM pedidos WHERE anuncio_id=? AND comprador_id=? "
        "AND status IN ('aguardando','confirmado','em_analise') ORDER BY criado_em DESC LIMIT 1",
        (anuncio_id, session["usuario_id"]),
    ).fetchone()
    if pedido_existente:
        flash("Você já possui um pedido ativo para este anúncio.", "erro")
        return redirect(url_for("pedidos"))

    if request.method == "POST":
        entrega = request.form.get("entrega", "retirada")
        observacao = request.form.get("observacao", "").strip()
        if entrega not in PEDIDO_ENTREGA:
            flash("Escolha uma forma de entrega valida.", "erro")
            return render_template("comprar.html", a=anuncio_item)
        if len(observacao) > 300:
            flash("A observacao deve ter no maximo 300 caracteres.", "erro")
            return render_template("comprar.html", a=anuncio_item)

        db.execute(
            "INSERT INTO pedidos (anuncio_id, comprador_id, vendedor_id, valor, status, entrega, observacao) "
            "VALUES (?,?,?,?,?,?,?)",
            (
                anuncio_id,
                session["usuario_id"],
                anuncio_item["usuario_id"],
                anuncio_item["preco"],
                "aguardando",
                entrega,
                observacao,
            ),
        )
        pedido_criado = db.execute(
            "SELECT p.*, a.titulo, comprador.nome AS comprador_nome, "
            "vendedor.nome AS vendedor_nome FROM pedidos p "
            "JOIN anuncios a ON a.id=p.anuncio_id "
            "JOIN usuarios comprador ON comprador.id=p.comprador_id "
            "JOIN usuarios vendedor ON vendedor.id=p.vendedor_id "
            "WHERE p.anuncio_id=? AND p.comprador_id=? "
            "ORDER BY p.id DESC LIMIT 1",
            (anuncio_id, session["usuario_id"]),
        ).fetchone()
        registrar_evento_pedido(
            db,
            pedido_criado["id"],
            "PEDIDO_CRIADO",
            "Pedido criado",
            session["usuario_id"],
            "comprador",
            estado_posterior="aguardando",
            dados_adicionais={"entrega": entrega},
        )
        db.commit()
        try:
            email_status = enviar_alerta_novo_pedido(
                pedido_criado, url_for("painel_admin", _external=True)
            )
        except Exception:
            app.logger.exception("Falha ao enviar alerta administrativo de pedido")
            email_status = "falhou"
        registrar_status_email_pedido(db, pedido_criado["id"], email_status)
        db.commit()
        flash("Pedido enviado! Aguarde a confirmação do vendedor.", "ok")
        return redirect(url_for("pedidos"))

    return render_template("comprar.html", a=anuncio_item)


@app.route("/pedidos")
def pedidos():
    if not logado():
        return redirect(url_for("login"))
    db = get_db()
    campos = (
        "SELECT p.*, a.titulo, a.foto, a.condicao, a.ativo AS anuncio_ativo, "
        "comprador.nome AS comprador_nome, comprador.whatsapp AS comprador_whatsapp, "
        "vendedor.nome AS vendedor_nome, vendedor.whatsapp AS vendedor_whatsapp, "
        "vendedor.mp_user_id AS vendedor_mp_user_id "
        "FROM pedidos p "
        "JOIN anuncios a ON a.id=p.anuncio_id "
        "JOIN usuarios comprador ON comprador.id=p.comprador_id "
        "JOIN usuarios vendedor ON vendedor.id=p.vendedor_id "
    )
    compras = db.execute(
        campos + "WHERE p.comprador_id=? ORDER BY p.criado_em DESC",
        (session["usuario_id"],),
    ).fetchall()
    vendas = db.execute(
        campos + "WHERE p.vendedor_id=? ORDER BY p.criado_em DESC",
        (loja_ativa_id(),),
    ).fetchall()
    eventos_por_pedido = buscar_eventos_pedidos(db, list(compras) + list(vendas))
    return render_template(
        "pedidos.html",
        compras=compras,
        vendas=vendas,
        eventos_por_pedido=eventos_por_pedido,
        problema_motivos=PROBLEMA_MOTIVOS,
    )


@app.route("/pedido/<int:pedido_id>/historico")
def historico_pedido(pedido_id):
    if not logado():
        return redirect(url_for("login"))
    db = get_db()
    pedido = db.execute(
        "SELECT p.*, a.titulo, comprador.nome AS comprador_nome, "
        "vendedor.nome AS vendedor_nome FROM pedidos p "
        "JOIN anuncios a ON a.id=p.anuncio_id "
        "JOIN usuarios comprador ON comprador.id=p.comprador_id "
        "JOIN usuarios vendedor ON vendedor.id=p.vendedor_id WHERE p.id=?",
        (pedido_id,),
    ).fetchone()
    if not pedido:
        abort(404)
    if session["usuario_id"] != pedido["comprador_id"] and not pode_administrar_loja(
        pedido["vendedor_id"]
    ):
        abort(403)
    eventos = buscar_eventos_pedidos(db, [pedido])[pedido_id]
    return render_template(
        "historico_pedido.html",
        p=pedido,
        eventos=eventos,
        problema_motivos=PROBLEMA_MOTIVOS,
    )


@app.route("/pedido/<int:pedido_id>/<acao>", methods=["POST"])
def atualizar_pedido(pedido_id, acao):
    if not logado():
        return redirect(url_for("login"))
    if acao not in {"confirmar", "recusar", "cancelar", "concluir", "problema"}:
        abort(404)

    db = get_db()
    pedido = db.execute("SELECT * FROM pedidos WHERE id=?", (pedido_id,)).fetchone()
    if not pedido:
        abort(404)

    usuario_id = session["usuario_id"]
    e_admin = admin()
    gerencia_vendedor = pode_administrar_loja(pedido["vendedor_id"])
    if acao in {"confirmar", "recusar"}:
        autorizado = gerencia_vendedor
        status_permitido = pedido["status"] == "aguardando"
    elif acao == "cancelar":
        autorizado = pedido["comprador_id"] == usuario_id or e_admin
        status_permitido = pedido["status"] in {
            "aguardando",
            "confirmado",
            "em_analise",
        }
    elif acao == "problema":
        autorizado = pedido["comprador_id"] == usuario_id or gerencia_vendedor
        status_permitido = pedido["status"] == "confirmado"
    else:
        autorizado = pedido["comprador_id"] == usuario_id or gerencia_vendedor
        status_permitido = pedido["status"] == "confirmado"

    if not autorizado:
        abort(403)
    if not status_permitido:
        flash("Este pedido não permite mais essa ação.", "erro")
        return redirect(url_for("pedidos"))
    if acao == "cancelar" and pedido["pagamento_status"] == "aprovado":
        flash(
            "Um pedido pago precisa passar pelo atendimento para ser cancelado.", "erro"
        )
        return redirect(url_for("pedidos"))
    motivo = request.form.get("motivo", "").strip()
    descricao_problema = request.form.get("descricao", "").strip()
    if acao == "problema":
        if motivo not in PROBLEMA_MOTIVOS:
            flash("Escolha o motivo do problema.", "erro")
            return redirect(url_for("pedidos"))
        if motivo == "OUTRO" and not descricao_problema:
            flash("Descreva o que aconteceu ao escolher Outro.", "erro")
            return redirect(url_for("pedidos"))
        if len(descricao_problema) > 1000:
            flash("A descrição do problema deve ter no máximo 1000 caracteres.", "erro")
            return redirect(url_for("pedidos"))

    papel = papel_usuario_pedido(pedido, usuario_id, e_admin)
    if gerencia_vendedor and pedido["vendedor_id"] != usuario_id and not e_admin:
        papel = "administrador_loja"
    try:
        if acao == "confirmar":
            atualizacao = db.execute(
                "UPDATE pedidos SET status='confirmado', atualizado_em=CURRENT_TIMESTAMP "
                "WHERE id=? AND status='aguardando'",
                (pedido_id,),
            )
            if atualizacao.rowcount != 1:
                db.rollback()
                flash("Este pedido já foi atualizado.", "erro")
                return redirect(url_for("pedidos"))
            reserva = db.execute(
                "UPDATE anuncios SET estoque=estoque-1, "
                "ativo=CASE WHEN estoque-1<=0 THEN 0 ELSE ativo END "
                "WHERE id=? AND estoque>0",
                (pedido["anuncio_id"],),
            )
            if reserva.rowcount != 1:
                db.rollback()
                db.execute(
                    "UPDATE pedidos SET status='recusado', atualizado_em=CURRENT_TIMESTAMP "
                    "WHERE id=? AND status='aguardando'",
                    (pedido_id,),
                )
                db.commit()
                flash("Pedido recusado porque o estoque acabou.", "erro")
                return redirect(url_for("pedidos"))
            estoque_atual = db.execute(
                "SELECT estoque FROM anuncios WHERE id=?", (pedido["anuncio_id"],)
            ).fetchone()["estoque"]
            registrar_evento_pedido(
                db,
                pedido_id,
                "VENDEDOR_CONFIRMOU",
                "Vendedor confirmou o pedido",
                usuario_id,
                papel,
                "aguardando",
                "confirmado",
            )
            registrar_evento_pedido(
                db,
                pedido_id,
                "ESTOQUE_RESERVADO",
                "Uma unidade foi reservada no estoque",
                papel_usuario="sistema",
                estado_anterior="confirmado",
                estado_posterior="confirmado",
                dados_adicionais={"estoque_restante": estoque_atual},
            )
            if estoque_atual <= 0:
                db.execute(
                    "UPDATE pedidos SET status='recusado', atualizado_em=CURRENT_TIMESTAMP "
                    "WHERE anuncio_id=? AND id<>? AND status='aguardando'",
                    (pedido["anuncio_id"], pedido_id),
                )
                mensagem = (
                    "Pedido confirmado. Última unidade reservada e anúncio pausado."
                )
            else:
                mensagem = "Pedido confirmado e 1 unidade reservada."
        elif acao == "recusar":
            recusa = db.execute(
                "UPDATE pedidos SET status='recusado', atualizado_em=CURRENT_TIMESTAMP "
                "WHERE id=? AND status='aguardando'",
                (pedido_id,),
            )
            if recusa.rowcount != 1:
                db.rollback()
                flash("Este pedido já foi atualizado.", "erro")
                return redirect(url_for("pedidos"))
            mensagem = "Pedido recusado."
        elif acao == "cancelar":
            estava_confirmado = pedido["status"] in {"confirmado", "em_analise"}
            cancelamento = db.execute(
                "UPDATE pedidos SET status='cancelado', atualizado_em=CURRENT_TIMESTAMP "
                "WHERE id=? AND status=?",
                (pedido_id, pedido["status"]),
            )
            if cancelamento.rowcount != 1:
                db.rollback()
                flash("Este pedido já foi atualizado.", "erro")
                return redirect(url_for("pedidos"))
            registrar_evento_pedido(
                db,
                pedido_id,
                "PEDIDO_CANCELADO",
                "Pedido cancelado",
                usuario_id,
                papel,
                pedido["status"],
                "cancelado",
            )
            if estava_confirmado:
                db.execute(
                    "UPDATE anuncios SET estoque=estoque+1 WHERE id=?",
                    (pedido["anuncio_id"],),
                )
                registrar_evento_pedido(
                    db,
                    pedido_id,
                    "ESTOQUE_DEVOLVIDO",
                    "Uma unidade foi devolvida ao estoque",
                    papel_usuario="sistema",
                    estado_anterior="cancelado",
                    estado_posterior="cancelado",
                )
                anuncio_moderado = db.execute(
                    "SELECT id FROM denuncias WHERE anuncio_id=? AND status='resolvida' LIMIT 1",
                    (pedido["anuncio_id"],),
                ).fetchone()
                vendedor = db.execute(
                    "SELECT ativo FROM usuarios WHERE id=?", (pedido["vendedor_id"],)
                ).fetchone()
                pode_reativar, _ = pode_criar_anuncio(pedido["vendedor_id"])
                if (
                    vendedor
                    and vendedor["ativo"]
                    and not anuncio_moderado
                    and pode_reativar
                ):
                    db.execute(
                        "UPDATE anuncios SET ativo=1 WHERE id=?",
                        (pedido["anuncio_id"],),
                    )
                    mensagem = "Pedido cancelado e anúncio disponibilizado novamente."
                else:
                    mensagem = "Pedido cancelado. O anúncio permaneceu pausado para revisão do vendedor."
            else:
                mensagem = "Pedido cancelado."
        elif acao == "problema":
            relato = db.execute(
                "UPDATE pedidos SET status='em_analise', problema_motivo=?, "
                "problema_descricao=?, problema_relator_id=?, problema_relator_papel=?, "
                "problema_relatado_em=CURRENT_TIMESTAMP, atualizado_em=CURRENT_TIMESTAMP "
                "WHERE id=? AND status='confirmado'",
                (motivo, descricao_problema, usuario_id, papel, pedido_id),
            )
            if relato.rowcount != 1:
                db.rollback()
                flash("Este pedido já foi atualizado.", "erro")
                return redirect(url_for("pedidos"))
            registrar_evento_pedido(
                db,
                pedido_id,
                "PROBLEMA_RELATADO",
                f"Problema relatado: {PROBLEMA_MOTIVOS[motivo]}",
                usuario_id,
                papel,
                "confirmado",
                "em_analise",
                dados_adicionais={"motivo": motivo},
            )
            registrar_evento_pedido(
                db,
                pedido_id,
                "PEDIDO_EM_ANALISE",
                "Pedido encaminhado para análise do administrador",
                papel_usuario="sistema",
                estado_anterior="confirmado",
                estado_posterior="em_analise",
            )
            mensagem = "Pedido enviado para análise do administrador."
        else:
            if e_admin:
                db.execute(
                    "UPDATE pedidos SET status='concluido', "
                    "vendedor_confirmou_em=COALESCE(vendedor_confirmou_em, CURRENT_TIMESTAMP), "
                    "comprador_confirmou_em=COALESCE(comprador_confirmou_em, CURRENT_TIMESTAMP), "
                    "atualizado_em=CURRENT_TIMESTAMP WHERE id=? AND status='confirmado'",
                    (pedido_id,),
                )
                registrar_evento_pedido(
                    db,
                    pedido_id,
                    "VENDA_MARCADA_COMO_REALIZADA",
                    "Administrador confirmou a realização da venda",
                    usuario_id,
                    "administrador",
                    "confirmado",
                    "confirmado",
                )
                registrar_evento_pedido(
                    db,
                    pedido_id,
                    "COMPRADOR_CONFIRMOU_RECEBIMENTO",
                    "Administrador confirmou o recebimento pelo comprador",
                    usuario_id,
                    "administrador",
                    "confirmado",
                    "confirmado",
                )
                mensagem = "Pedido concluído pelo administrador."
            else:
                comprador_agiu = pedido["comprador_id"] == usuario_id
                campo = (
                    "comprador_confirmou_em"
                    if comprador_agiu
                    else "vendedor_confirmou_em"
                )
                db.execute(
                    f"UPDATE pedidos SET {campo}=COALESCE({campo}, CURRENT_TIMESTAMP), "
                    "atualizado_em=CURRENT_TIMESTAMP WHERE id=? AND status='confirmado'",
                    (pedido_id,),
                )
                if comprador_agiu:
                    registrar_evento_pedido(
                        db,
                        pedido_id,
                        "COMPRADOR_CONFIRMOU_RECEBIMENTO",
                        "Comprador informou que recebeu o produto",
                        usuario_id,
                        "comprador",
                        "confirmado",
                        "confirmado",
                    )
                else:
                    registrar_evento_pedido(
                        db,
                        pedido_id,
                        "VENDA_MARCADA_COMO_REALIZADA",
                        "Vendedor marcou a venda como realizada",
                        usuario_id,
                        "vendedor",
                        "confirmado",
                        "confirmado",
                    )
                mensagem = (
                    "Recebimento registrado. Aguardando confirmação do vendedor."
                    if comprador_agiu
                    else "Venda registrada. Aguardando confirmação do comprador."
                )
            pedido_atualizado = db.execute(
                "SELECT vendedor_confirmou_em, comprador_confirmou_em FROM pedidos WHERE id=?",
                (pedido_id,),
            ).fetchone()
            if (
                pedido_atualizado["vendedor_confirmou_em"]
                and pedido_atualizado["comprador_confirmou_em"]
            ):
                db.execute(
                    "UPDATE pedidos SET status='concluido', atualizado_em=CURRENT_TIMESTAMP "
                    "WHERE id=? AND status='confirmado'",
                    (pedido_id,),
                )
                registrar_evento_pedido(
                    db,
                    pedido_id,
                    "PEDIDO_CONCLUIDO",
                    "Pedido concluído",
                    papel_usuario="sistema",
                    estado_anterior="confirmado",
                    estado_posterior="concluido",
                )
                if not e_admin:
                    mensagem = "Pedido concluído com confirmação dos dois lados."

        db.commit()
    except Exception:
        db.rollback()
        app.logger.exception("Falha ao atualizar pedido %s", pedido_id)
        flash("Não foi possível atualizar o pedido. Tente novamente.", "erro")
        return redirect(url_for("pedidos"))
    flash(mensagem, "ok")
    return redirect(url_for("pedidos"))


@app.route("/pedido/<int:pedido_id>/pagar-mercadopago", methods=["POST"])
def pagar_mercadopago(pedido_id):
    if not logado():
        return redirect(url_for("login"))
    if not mercadopago_pagamentos_configurados():
        flash("Os pagamentos pelo Mercado Pago ainda estao em ativacao.", "erro")
        return redirect(url_for("pedidos"))
    db = get_db()
    pedido = db.execute(
        "SELECT p.*, a.titulo, a.foto, vendedor.mp_user_id "
        "FROM pedidos p JOIN anuncios a ON a.id=p.anuncio_id "
        "JOIN usuarios vendedor ON vendedor.id=p.vendedor_id WHERE p.id=?",
        (pedido_id,),
    ).fetchone()
    if not pedido or pedido["comprador_id"] != session["usuario_id"]:
        abort(404)
    if pedido["status"] != "confirmado":
        flash("O vendedor precisa confirmar o pedido antes do pagamento.", "erro")
        return redirect(url_for("pedidos"))
    if pedido["pagamento_status"] == "aprovado":
        flash("Este pedido ja esta pago.", "ok")
        return redirect(url_for("pedidos"))
    if not pedido["mp_user_id"]:
        flash("O vendedor ainda nao conectou o Mercado Pago.", "erro")
        return redirect(url_for("pedidos"))

    try:
        access_token = obter_token_vendedor(pedido["vendedor_id"])
        valor = preco_decimal(pedido["valor"])
        comissao = (valor * MARKETPLACE_FEE_PERCENT / Decimal("100")).quantize(
            Decimal("0.01")
        )
        item = {
            "id": str(pedido["anuncio_id"]),
            "title": pedido["titulo"][:120],
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": float(valor),
        }
        imagem = foto_url(pedido["foto"], 700) if pedido["foto"] else ""
        if imagem.startswith("https://"):
            item["picture_url"] = imagem
        retorno_base = url_for(
            "mercadopago_retorno", pedido_id=pedido_id, _external=True
        )
        preferencia = {
            "items": [item],
            "external_reference": f"MC-PEDIDO-{pedido_id}",
            "back_urls": {
                "success": f"{retorno_base}&resultado=sucesso",
                "pending": f"{retorno_base}&resultado=pendente",
                "failure": f"{retorno_base}&resultado=falha",
            },
            "auto_return": "approved",
            "notification_url": url_for("mercadopago_webhook", _external=True),
            "statement_descriptor": "MERCADOCOLATINA",
            "metadata": {"pedido_id": pedido_id},
        }
        if comissao > 0:
            preferencia["marketplace_fee"] = float(comissao)
        resposta = criar_preferencia(access_token, preferencia)
        checkout_url = resposta.get("init_point")
        if not checkout_url:
            raise MercadoPagoError("Checkout indisponivel.")
        db.execute(
            "UPDATE pedidos SET pagamento_status='aguardando', mp_preference_id=?, "
            "mp_checkout_url=?, comissao=?, atualizado_em=CURRENT_TIMESTAMP WHERE id=?",
            (resposta.get("id"), checkout_url, f"{comissao:.2f}", pedido_id),
        )
        db.commit()
        return redirect(checkout_url)
    except (MercadoPagoError, ValueError):
        app.logger.exception("Falha ao criar checkout Mercado Pago")
        flash("Nao foi possivel abrir o pagamento. Tente novamente.", "erro")
        return redirect(url_for("pedidos"))


@app.route("/mercadopago/retorno")
def mercadopago_retorno():
    if not logado():
        return redirect(url_for("login"))
    try:
        pedido_id = int(request.args.get("pedido_id", "0"))
    except ValueError:
        pedido_id = 0
    db = get_db()
    pedido = db.execute("SELECT * FROM pedidos WHERE id=?", (pedido_id,)).fetchone()
    if not pedido or pedido["comprador_id"] != session["usuario_id"]:
        abort(404)

    payment_id = request.args.get("payment_id") or request.args.get("collection_id")
    if payment_id and payment_id != "null":
        try:
            access_token = obter_token_vendedor(pedido["vendedor_id"])
            pagamento = consultar_pagamento(access_token, payment_id)
            atualizar_pagamento_do_pedido(db, pagamento)
        except MercadoPagoError:
            app.logger.exception("Falha ao conferir retorno do Mercado Pago")

    pedido_atualizado = db.execute(
        "SELECT pagamento_status FROM pedidos WHERE id=?", (pedido_id,)
    ).fetchone()
    if pedido_atualizado and pedido_atualizado["pagamento_status"] == "aprovado":
        flash("Pagamento aprovado pelo Mercado Pago!", "ok")
    elif request.args.get("resultado") == "pendente":
        flash("Pagamento em analise pelo Mercado Pago.", "ok")
    else:
        flash("Pagamento nao concluido. Voce pode tentar novamente.", "erro")
    return redirect(url_for("pedidos"))


@app.route("/mercadopago/webhook", methods=["POST"])
def mercadopago_webhook():
    payload = request.get_json(silent=True) or {}
    data_id = request.args.get("data.id") or (payload.get("data") or {}).get("id")
    if not data_id:
        return "", 200
    if not webhook_valido(
        request.headers.get("x-signature"),
        request.headers.get("x-request-id"),
        data_id,
    ):
        return "", 401
    if payload.get("type") != "payment":
        return "", 200

    mp_user_id = payload.get("user_id")
    vendedor = (
        get_db()
        .execute("SELECT id FROM usuarios WHERE mp_user_id=?", (str(mp_user_id),))
        .fetchone()
    )
    if not vendedor:
        return "", 200
    try:
        access_token = obter_token_vendedor(vendedor["id"])
        pagamento = consultar_pagamento(access_token, data_id)
        atualizar_pagamento_do_pedido(get_db(), pagamento)
    except MercadoPagoError:
        app.logger.exception("Falha ao processar webhook Mercado Pago")
        return "", 503
    return "", 200


@app.route("/seguranca")
def pagina_seguranca():
    return render_template(
        "pagina_info.html",
        titulo="Segurança nas negociações",
        resumo="Cuidados simples ajudam compradores e vendedores a negociar com mais tranquilidade.",
        secoes=[
            (
                "Converse com clareza",
                "Confirme o estado do produto, o valor final, a forma de pagamento e o local de entrega antes de fechar o negócio.",
            ),
            (
                "Prefira locais seguros",
                "Quando possível, encontre a outra pessoa em local público, movimentado e durante o dia. Avise alguém de confiança.",
            ),
            (
                "Proteja seus dados",
                "Nunca compartilhe senhas, códigos recebidos por mensagem, dados bancários completos ou documentos sem necessidade.",
            ),
            (
                "Desconfie de pressa ou vantagem excessiva",
                "Preços muito abaixo do mercado, cobranças antecipadas e pedidos para sair dos canais combinados podem indicar fraude.",
            ),
        ],
    )


@app.route("/privacidade")
def pagina_privacidade():
    return render_template(
        "pagina_info.html",
        titulo="Privacidade",
        resumo="Tratamos apenas os dados necessários para manter sua conta e permitir o contato entre compradores e vendedores.",
        secoes=[
            (
                "Dados utilizados",
                "Nome, nome de usuário, senha protegida, WhatsApp, informações dos anúncios, histórico dos pedidos e situação dos pagamentos realizados.",
            ),
            (
                "Finalidade",
                "Os dados são usados para autenticação, administração da conta, publicação dos anúncios, organização dos pedidos, contato entre as partes e confirmação dos pagamentos.",
            ),
            (
                "Mercado Pago",
                "Quando o vendedor conecta sua conta, guardamos de forma criptografada apenas as credenciais técnicas necessárias para processar e conferir pagamentos. Dados de cartão não passam pelo Mercado Colatina.",
            ),
            (
                "Assistente Neo",
                "Quando o vendedor escolhe usar o Neo, o relato digitado é enviado ao provedor de inteligência artificial para gerar um rascunho. Não envie documentos, senhas, dados bancários ou informações pessoais de terceiros. O uso é opcional e o vendedor deve revisar o resultado.",
            ),
            (
                "Proteção",
                "Senhas e credenciais de integração não são armazenadas em texto legível. O acesso administrativo deve ser restrito e monitorado.",
            ),
            (
                "Seus direitos",
                "O titular pode solicitar correção ou exclusão dos seus dados ao administrador do Mercado Colatina.",
            ),
        ],
    )


@app.route("/termos")
def pagina_termos():
    return render_template(
        "pagina_info.html",
        titulo="Termos de uso",
        resumo="O Mercado Colatina aproxima compradores e vendedores, mas não participa diretamente das negociações.",
        secoes=[
            (
                "Responsabilidade do anunciante",
                "O anunciante deve fornecer informações verdadeiras, manter o anúncio atualizado e possuir legitimidade para vender o item ou serviço.",
            ),
            (
                "Conteúdo proibido",
                "Não são permitidos produtos ilegais, conteúdo enganoso, ofensivo, perigoso ou que viole direitos de terceiros.",
            ),
            (
                "Pedidos entre usuários",
                "O pedido registra o interesse de compra e permite que o vendedor confirme a disponibilidade. Entrega, garantia e demais condições devem ser combinadas entre comprador e vendedor.",
            ),
            (
                "Pagamentos",
                "Quando disponível, o pagamento é processado pelo Mercado Pago diretamente na conta conectada pelo vendedor. Taxas, análises, estornos e contestações seguem também as regras do Mercado Pago. O Mercado Colatina não recebe o valor do produto.",
            ),
            (
                "Moderação",
                "Anúncios e contas que violem estas regras podem ser ocultados ou desativados para proteger a comunidade.",
            ),
            (
                "Conteúdo assistido por IA",
                "O Neo apenas sugere um rascunho. O anunciante continua responsável por revisar a exatidão, completar informações ausentes e garantir que o conteúdo e o produto respeitem estes termos.",
            ),
        ],
    )


@app.route("/deletar/<int:anuncio_id>", methods=["POST"])
def deletar_anuncio(anuncio_id):
    if not logado():
        return redirect(url_for("login"))
    db = get_db()
    anuncio_item = db.execute(
        "SELECT * FROM anuncios WHERE id=? AND excluido_em IS NULL",
        (anuncio_id,),
    ).fetchone()
    if anuncio_item and pode_administrar_loja(anuncio_item["usuario_id"]):
        db.execute(
            "UPDATE anuncios SET ativo=0, excluido_em=CURRENT_TIMESTAMP WHERE id=?",
            (anuncio_id,),
        )
        db.commit()
        flash("Produto excluído com sucesso.", "ok")
    return redirect(url_for("meus_anuncios"))


def montar_cockpit_executivo(db):
    commit = (
        os.environ.get("RENDER_GIT_COMMIT") or os.environ.get("GIT_COMMIT") or ""
    ).strip()
    ci_status_original = os.environ.get("CI_STATUS", "").strip().lower()
    ci_status_rotulos = {
        "success": "Aprovado",
        "passed": "Aprovado",
        "approved": "Aprovado",
        "failure": "Falhou",
        "failed": "Falhou",
        "pending": "Em andamento",
        "running": "Em andamento",
    }
    ci_status = ci_status_rotulos.get(
        ci_status_original,
        os.environ.get("CI_STATUS", "").strip() or "Não informado",
    )
    em_render = bool(
        os.environ.get("RENDER")
        or os.environ.get("RENDER_SERVICE_ID")
        or os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    )
    ambiente = "Produção · Render" if em_render else FLASK_ENV.capitalize()
    deploy = os.environ.get("RENDER_DEPLOY_ID", "").strip()
    if not deploy and commit:
        deploy = f"Versão {commit[:12]}"

    metricas = {
        "anuncios_ativos": db.execute(
            "SELECT COUNT(*) FROM anuncios WHERE ativo=1"
        ).fetchone()[0],
        "usuarios_cadastrados": db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[
            0
        ],
        "lojas_cadastradas": db.execute(
            "SELECT COUNT(*) FROM usuarios WHERE TRIM(COALESCE(loja_nome, ''))<>''"
        ).fetchone()[0],
        "pedidos": db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0],
        "solicitacoes_compra": db.execute(
            "SELECT COUNT(*) FROM pedidos WHERE status='aguardando'"
        ).fetchone()[0],
    }

    ultimos_anuncios = db.execute(
        "SELECT a.id, a.titulo, a.ativo, a.criado_em, u.nome AS vendedor_nome "
        "FROM anuncios a JOIN usuarios u ON u.id=a.usuario_id "
        "ORDER BY a.criado_em DESC, a.id DESC LIMIT 5"
    ).fetchall()
    ultimos_usuarios = db.execute(
        "SELECT id, nome, username, ativo, criado_em FROM usuarios "
        "ORDER BY criado_em DESC, id DESC LIMIT 5"
    ).fetchall()
    ultimos_pedidos = db.execute(
        "SELECT p.id, p.status, p.valor, p.criado_em, a.titulo, "
        "comprador.nome AS comprador_nome, vendedor.nome AS vendedor_nome "
        "FROM pedidos p "
        "JOIN anuncios a ON a.id=p.anuncio_id "
        "JOIN usuarios comprador ON comprador.id=p.comprador_id "
        "JOIN usuarios vendedor ON vendedor.id=p.vendedor_id "
        "ORDER BY p.criado_em DESC, p.id DESC LIMIT 5"
    ).fetchall()

    denuncias_pendentes = db.execute(
        "SELECT COUNT(*) FROM denuncias WHERE status='pendente'"
    ).fetchone()[0]
    pedidos_em_analise = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status='em_analise'"
    ).fetchone()[0]
    alertas = []
    if denuncias_pendentes:
        alertas.append(
            {
                "titulo": "Denúncias aguardando análise",
                "descricao": (
                    f"{denuncias_pendentes} denúncia"
                    f"{'s' if denuncias_pendentes != 1 else ''} pendente"
                    f"{'s' if denuncias_pendentes != 1 else ''} na administração."
                ),
                "tipo": "warning",
            }
        )
    if pedidos_em_analise:
        alertas.append(
            {
                "titulo": "Pedidos em análise",
                "descricao": (
                    f"{pedidos_em_analise} pedido"
                    f"{'s' if pedidos_em_analise != 1 else ''} requer"
                    f"{'em' if pedidos_em_analise != 1 else ''} acompanhamento."
                ),
                "tipo": "danger",
            }
        )
    if not email_configurado():
        alertas.append(
            {
                "titulo": "Alertas por e-mail indisponíveis",
                "descricao": "A administração ainda não possui envio de e-mail ativo.",
                "tipo": "info",
            }
        )

    if alertas:
        indicador_atencao = alertas[0]["titulo"]
        indicador_contexto = alertas[0]["descricao"]
    elif metricas["solicitacoes_compra"]:
        indicador_atencao = "Solicitações aguardando vendedor"
        indicador_contexto = (
            f"{metricas['solicitacoes_compra']} "
            f"{'solicitações' if metricas['solicitacoes_compra'] != 1 else 'solicitação'} "
            "na etapa inicial."
        )
    else:
        indicador_atencao = "Operação sem alertas importantes"
        indicador_contexto = "Nenhum problema importante encontrado."

    return {
        "gerado_em": datetime.now(timezone.utc).strftime("%d/%m/%Y · %H:%M UTC"),
        "saude": {
            "aplicacao": "Operacional",
            "health_check": "HTTP 200",
            "ultimo_deploy": deploy or "Não informado",
            "ultimo_commit": commit[:12] if commit else "Não informado",
            "ci_status": ci_status,
            "testes": contar_testes_automatizados(),
            "ambiente": ambiente,
        },
        "metricas": metricas,
        "ultimos_anuncios": ultimos_anuncios,
        "ultimos_usuarios": ultimos_usuarios,
        "ultimos_pedidos": ultimos_pedidos,
        "alertas": alertas,
        "indicador_atencao": indicador_atencao,
        "indicador_contexto": indicador_contexto,
    }


def montar_dashboard_executivo(db):
    dashboard = montar_cockpit_executivo(db)

    categorias_agrupadas = {}
    categorias = db.execute(
        "SELECT categoria, COUNT(*) AS total FROM anuncios "
        "WHERE ativo=1 GROUP BY categoria"
    ).fetchall()
    for categoria in categorias:
        nome = categoria_label(categoria["categoria"])
        categorias_agrupadas[nome] = (
            categorias_agrupadas.get(nome, 0) + categoria["total"]
        )

    dashboard["categorias_mais_utilizadas"] = [
        {"nome": nome, "total": total}
        for nome, total in sorted(
            categorias_agrupadas.items(), key=lambda item: (-item[1], item[0])
        )[:5]
    ]
    dashboard["produtos_mais_recentes"] = db.execute(
        "SELECT a.id, a.titulo, a.preco, a.categoria, a.criado_em, "
        "u.id AS vendedor_id, u.nome AS vendedor_nome, u.loja_nome "
        "FROM anuncios a JOIN usuarios u ON u.id=a.usuario_id "
        "WHERE a.ativo=1 ORDER BY a.criado_em DESC, a.id DESC LIMIT 5"
    ).fetchall()
    dashboard["lojas_mais_recentes"] = db.execute(
        "SELECT id, nome, loja_nome, loja_bairro, criado_em FROM usuarios "
        "WHERE TRIM(COALESCE(loja_nome, ''))<>'' "
        "ORDER BY criado_em DESC, id DESC LIMIT 5"
    ).fetchall()
    return dashboard


@app.route("/admin")
def painel_admin():
    if not admin():
        return redirect(url_for("index"))
    db = get_db()
    if request.args.get("visao") == "dashboard":
        return render_template(
            "dashboard_executivo.html",
            dashboard=montar_dashboard_executivo(db),
            formatar_data_cockpit=formatar_data_cockpit,
        )
    if request.args.get("visao") == "cockpit":
        return render_template(
            "cockpit.html",
            cockpit=montar_cockpit_executivo(db),
            formatar_data_cockpit=formatar_data_cockpit,
        )
    usuarios_todos = db.execute(
        "SELECT * FROM usuarios ORDER BY criado_em DESC"
    ).fetchall()
    usuarios_filtro = request.args.get("usuarios_filtro", "todos")
    if usuarios_filtro not in {"todos", "fundadores"}:
        usuarios_filtro = "todos"
    fundadores = [usuario for usuario in usuarios_todos if usuario["fundador"]]
    usuarios = fundadores if usuarios_filtro == "fundadores" else usuarios_todos
    anuncios = db.execute(
        "SELECT a.*, u.nome AS vendedor_nome "
        "FROM anuncios a "
        "JOIN usuarios u ON a.usuario_id=u.id "
        "ORDER BY a.criado_em DESC"
    ).fetchall()
    pagamentos = db.execute(
        "SELECT p.*, u.nome AS usuario_nome, u.username, u.whatsapp "
        "FROM pagamentos p JOIN usuarios u ON p.usuario_id=u.id "
        "ORDER BY p.criado_em DESC"
    ).fetchall()
    pedidos_admin = db.execute(
        "SELECT p.*, a.titulo, comprador.nome AS comprador_nome, vendedor.nome AS vendedor_nome "
        "FROM pedidos p "
        "JOIN anuncios a ON a.id=p.anuncio_id "
        "JOIN usuarios comprador ON comprador.id=p.comprador_id "
        "JOIN usuarios vendedor ON vendedor.id=p.vendedor_id "
        "ORDER BY p.criado_em DESC"
    ).fetchall()
    pedidos_atencao = [
        pedido
        for pedido in pedidos_admin
        if pedido["status"] in {"aguardando", "confirmado", "em_analise"}
    ]
    eventos_pedidos_admin = buscar_eventos_pedidos(db, pedidos_admin)
    denuncias = db.execute(
        "SELECT d.*, a.titulo, a.ativo AS anuncio_ativo, "
        "denunciante.nome AS denunciante_nome, vendedor.nome AS vendedor_nome "
        "FROM denuncias d "
        "JOIN anuncios a ON a.id=d.anuncio_id "
        "JOIN usuarios denunciante ON denunciante.id=d.denunciante_id "
        "JOIN usuarios vendedor ON vendedor.id=a.usuario_id "
        "ORDER BY CASE WHEN d.status='pendente' THEN 0 ELSE 1 END, d.criado_em DESC"
    ).fetchall()
    comunicados = db.execute(
        "SELECT c.*, u.nome AS autor_nome FROM comunicados c "
        "JOIN usuarios u ON u.id=c.criado_por "
        "ORDER BY c.criado_em DESC, c.id DESC"
    ).fetchall()
    metricas = {
        "usuarios_ativos": db.execute(
            "SELECT COUNT(*) FROM usuarios WHERE ativo=1"
        ).fetchone()[0],
        "anuncios_ativos": db.execute(
            "SELECT COUNT(*) FROM anuncios WHERE ativo=1"
        ).fetchone()[0],
        "contatos": db.execute(
            "SELECT COALESCE(SUM(contatos_whatsapp),0) FROM anuncios"
        ).fetchone()[0],
        "pedidos": db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0],
        "denuncias_pendentes": db.execute(
            "SELECT COUNT(*) FROM denuncias WHERE status='pendente'"
        ).fetchone()[0],
        "fundadores": len(fundadores),
    }
    return render_template(
        "admin.html",
        usuarios=usuarios,
        fundadores=fundadores,
        usuarios_filtro=usuarios_filtro,
        limite_fundadores=LIMITE_FUNDADORES,
        anuncios=anuncios,
        pagamentos=pagamentos,
        pedidos=pedidos_admin,
        eventos_por_pedido=eventos_pedidos_admin,
        problema_motivos=PROBLEMA_MOTIVOS,
        pedidos_atencao=pedidos_atencao,
        admin_notification_email=destinatario_admin(),
        admin_email_configurado=email_configurado(),
        denuncias=denuncias,
        denuncia_motivos=DENUNCIA_MOTIVOS,
        comunicado_tipos=COMUNICADO_TIPOS,
        comunicados=comunicados,
        metricas=metricas,
    )


@app.route("/admin/reputacao/<int:usuario_id>")
def admin_reputacao_usuario(usuario_id):
    if not admin():
        return redirect(url_for("index"))
    db = get_db()
    usuario = db.execute(
        "SELECT id, nome, username, criado_em, ultimo_acesso_em, loja_verificada, "
        "fundador, fundador_desde "
        "FROM usuarios WHERE id=?",
        (usuario_id,),
    ).fetchone()
    if not usuario:
        abort(404)
    reputacao = calcular_reputacao_usuario(db, usuario)
    return render_template(
        "reputacao_usuario.html",
        usuario=usuario,
        reputacao_vendedor=reputacao["vendedor"],
        reputacao_comprador=reputacao["comprador"],
    )


@app.route("/admin/email/teste", methods=["POST"])
def admin_testar_email():
    if not admin():
        return redirect(url_for("index"))

    try:
        email_status = enviar_teste_admin(url_for("painel_admin", _external=True))
    except Exception:
        app.logger.exception("Falha ao enviar e-mail administrativo de teste")
        email_status = "falhou"

    if email_status == "enviado":
        flash("E-mail de teste enviado para o administrador.", "ok")
    elif email_status == "aguardando_configuracao":
        flash("Configure o e-mail administrativo antes de enviar o teste.", "erro")
    else:
        flash(
            "Nao foi possivel enviar o e-mail de teste. Confira o Render e o Gmail.",
            "erro",
        )
    return redirect(url_for("painel_admin"))


@app.route("/admin/pedido/<int:pedido_id>/reenviar-email", methods=["POST"])
def admin_reenviar_email_pedido(pedido_id):
    if not admin():
        return redirect(url_for("index"))

    db = get_db()
    pedido = buscar_pedido_admin(db, pedido_id)
    if not pedido:
        abort(404)

    try:
        email_status = enviar_alerta_novo_pedido(
            pedido, url_for("painel_admin", _external=True)
        )
    except Exception:
        app.logger.exception("Falha ao reenviar alerta administrativo de pedido")
        email_status = "falhou"

    registrar_status_email_pedido(db, pedido_id, email_status)
    db.commit()
    if email_status == "enviado":
        flash(f"Alerta do pedido #{pedido_id} reenviado por e-mail.", "ok")
    elif email_status == "aguardando_configuracao":
        flash("Configure o e-mail administrativo antes de reenviar alertas.", "erro")
    else:
        flash(f"Nao foi possivel reenviar o alerta do pedido #{pedido_id}.", "erro")
    return redirect(url_for("painel_admin") + f"#pedido-{pedido_id}")


@app.route("/admin/comunicado", methods=["POST"])
def admin_criar_comunicado():
    if not admin():
        return redirect(url_for("index"))

    titulo = request.form.get("titulo", "").strip()
    mensagem = request.form.get("mensagem", "").strip()
    tipo = request.form.get("tipo", "informacao")
    if not 3 <= len(titulo) <= 80:
        flash("O título do comunicado deve ter entre 3 e 80 caracteres.", "erro")
        return redirect(url_for("painel_admin"))
    if not 5 <= len(mensagem) <= 500:
        flash("A mensagem deve ter entre 5 e 500 caracteres.", "erro")
        return redirect(url_for("painel_admin"))
    if tipo not in COMUNICADO_TIPOS:
        flash("Escolha um tipo de comunicado válido.", "erro")
        return redirect(url_for("painel_admin"))

    db = get_db()
    db.execute(
        "UPDATE comunicados SET ativo=0, desativado_em=CURRENT_TIMESTAMP WHERE ativo=1"
    )
    db.execute(
        "INSERT INTO comunicados (titulo, mensagem, tipo, criado_por) VALUES (?,?,?,?)",
        (titulo, mensagem, tipo, session["usuario_id"]),
    )
    db.commit()
    flash("Comunicado publicado para todos os usuários.", "ok")
    return redirect(url_for("painel_admin"))


@app.route("/admin/comunicado/<int:comunicado_id>/toggle", methods=["POST"])
def admin_toggle_comunicado(comunicado_id):
    if not admin():
        return redirect(url_for("index"))

    db = get_db()
    comunicado = db.execute(
        "SELECT id, ativo FROM comunicados WHERE id=?", (comunicado_id,)
    ).fetchone()
    if not comunicado:
        abort(404)

    if comunicado["ativo"]:
        db.execute(
            "UPDATE comunicados SET ativo=0, desativado_em=CURRENT_TIMESTAMP "
            "WHERE id=?",
            (comunicado_id,),
        )
        mensagem = "Comunicado arquivado."
    else:
        db.execute(
            "UPDATE comunicados SET ativo=0, desativado_em=CURRENT_TIMESTAMP "
            "WHERE ativo=1"
        )
        db.execute(
            "UPDATE comunicados SET ativo=1, desativado_em=NULL WHERE id=?",
            (comunicado_id,),
        )
        mensagem = "Comunicado reativado para todos os usuários."
    db.commit()
    flash(mensagem, "ok")
    return redirect(url_for("painel_admin"))


@app.route("/ajuda")
def pagina_ajuda():
    numero = limpar_whatsapp(SUPPORT_WHATSAPP)
    if not numero.startswith("55"):
        numero = f"55{numero}"
    mensagem = quote("Olá! Preciso de ajuda com o Mercado Colatina.")
    return render_template(
        "ajuda.html",
        suporte_url=f"https://wa.me/{numero}?text={mensagem}",
    )


@app.route("/admin/denuncia/<int:denuncia_id>/<acao>", methods=["POST"])
def admin_processar_denuncia(denuncia_id, acao):
    if not admin():
        return redirect(url_for("index"))
    if acao not in {"ocultar", "descartar"}:
        abort(404)

    db = get_db()
    denuncia = db.execute(
        "SELECT id, anuncio_id, status FROM denuncias WHERE id=?",
        (denuncia_id,),
    ).fetchone()
    if not denuncia:
        abort(404)
    if denuncia["status"] != "pendente":
        flash("Esta denuncia ja foi analisada.", "erro")
        return redirect(url_for("painel_admin"))

    if acao == "ocultar":
        db.execute("UPDATE anuncios SET ativo=0 WHERE id=?", (denuncia["anuncio_id"],))
        db.execute(
            "UPDATE denuncias SET status='resolvida', resolvido_em=CURRENT_TIMESTAMP, "
            "resolvido_por=? WHERE anuncio_id=? AND status='pendente'",
            (session["usuario_id"], denuncia["anuncio_id"]),
        )
        mensagem = "Anúncio ocultado e denúncia resolvida."
    else:
        mensagem = "Denuncia descartada. O anuncio foi mantido."
        db.execute(
            "UPDATE denuncias SET status=?, resolvido_em=CURRENT_TIMESTAMP, resolvido_por=? WHERE id=?",
            ("descartada", session["usuario_id"], denuncia_id),
        )
    db.commit()
    flash(mensagem, "ok")
    return redirect(url_for("painel_admin"))


@app.route("/admin/pagamento/<int:pagamento_id>/<acao>", methods=["POST"])
def admin_processar_pagamento(pagamento_id, acao):
    if not admin():
        return redirect(url_for("index"))
    if acao not in {"aprovar", "recusar"}:
        abort(404)

    db = get_db()
    pagamento = db.execute(
        "SELECT * FROM pagamentos WHERE id=?",
        (pagamento_id,),
    ).fetchone()
    if not pagamento:
        abort(404)
    if pagamento["status"] != "pendente":
        flash("Esta solicitação já foi processada.", "erro")
        return redirect(url_for("painel_admin"))

    if acao == "aprovar":
        usuario = db.execute(
            "SELECT plano_expira FROM usuarios WHERE id=?",
            (pagamento["usuario_id"],),
        ).fetchone()
        inicio = date.today()
        if usuario and usuario["plano_expira"]:
            try:
                expira_atual = date.fromisoformat(str(usuario["plano_expira"])[:10])
                if expira_atual > inicio:
                    inicio = expira_atual
            except ValueError:
                pass
        nova_expiracao = (inicio + timedelta(days=30)).isoformat()
        db.execute(
            "UPDATE usuarios SET plano_ativo=1, plano_expira=? WHERE id=?",
            (nova_expiracao, pagamento["usuario_id"]),
        )
        novo_status = "aprovado"
        mensagem = "Pagamento aprovado e plano ativado por 30 dias."
    else:
        novo_status = "recusado"
        mensagem = "Solicitação de pagamento recusada."

    db.execute(
        "UPDATE pagamentos SET status=?, atualizado_em=CURRENT_TIMESTAMP WHERE id=?",
        (novo_status, pagamento_id),
    )
    db.commit()
    flash(mensagem, "ok")
    return redirect(url_for("painel_admin"))


@app.route("/admin/usuario", methods=["POST"])
def admin_criar_usuario():
    if not admin():
        return redirect(url_for("index"))

    nome = request.form["nome"].strip()
    username = request.form["username"].strip()
    senha = request.form["senha"].strip()
    whatsapp = limpar_whatsapp(request.form["whatsapp"].strip())
    is_admin = 1 if request.form.get("is_admin") else 0
    erro = validar_usuario(nome, username, senha, whatsapp)
    if erro:
        flash(erro, "erro")
        return redirect(url_for("painel_admin"))
    db = get_db()
    try:
        fundador, fundador_origem = reservar_selo_fundador(db)
        db.execute(
            "INSERT INTO usuarios (nome, username, senha, whatsapp, is_admin, "
            "fundador, fundador_desde, fundador_origem) VALUES (?,?,?,?,?,?,"
            "CASE WHEN ?=1 THEN CURRENT_TIMESTAMP ELSE NULL END,?)",
            (
                nome,
                username,
                generate_password_hash(senha),
                whatsapp,
                is_admin,
                fundador,
                fundador,
                fundador_origem,
            ),
        )
        db.commit()
        mensagem = f"Usuario {nome} cadastrado."
        if fundador:
            mensagem += " Selo de Fundador concedido automaticamente."
        flash(mensagem, "ok")
    except Exception:
        db.rollback()
        flash("Username ja existe.", "erro")
    return redirect(url_for("painel_admin"))


@app.route("/admin/usuario/<int:usuario_id>/fundador", methods=["POST"])
def admin_alterar_fundador(usuario_id):
    if not admin():
        return redirect(url_for("index"))

    acao = request.form.get("acao", "")
    if acao not in {"conceder", "remover"}:
        abort(400)
    db = get_db()
    usuario = db.execute(
        "SELECT id, nome, fundador FROM usuarios WHERE id=?", (usuario_id,)
    ).fetchone()
    if not usuario:
        abort(404)

    if acao == "conceder":
        db.execute(
            "UPDATE usuarios SET fundador=1, "
            "fundador_desde=COALESCE(fundador_desde, CURRENT_TIMESTAMP), "
            "fundador_origem=COALESCE(fundador_origem, 'manual'), "
            "fundador_removido_em=NULL, fundador_alterado_por=? WHERE id=?",
            (session["usuario_id"], usuario_id),
        )
        mensagem = f"Selo de Fundador concedido a {usuario['nome']}."
    else:
        db.execute(
            "UPDATE usuarios SET fundador=0, fundador_removido_em=CURRENT_TIMESTAMP, "
            "fundador_alterado_por=? WHERE id=?",
            (session["usuario_id"], usuario_id),
        )
        mensagem = f"Selo de Fundador removido de {usuario['nome']}."
    db.commit()
    flash(mensagem, "ok")
    return redirect(url_for("painel_admin", usuarios_filtro="fundadores"))


@app.route("/admin/usuario/<int:usuario_id>/toggle", methods=["POST"])
def admin_toggle_usuario(usuario_id):
    if not admin():
        return redirect(url_for("index"))
    if usuario_id == session["usuario_id"]:
        flash(
            "Por segurança, você não pode desativar sua própria conta administrativa.",
            "erro",
        )
        return redirect(url_for("painel_admin"))
    db = get_db()
    usuario = db.execute(
        "SELECT ativo FROM usuarios WHERE id=?",
        (usuario_id,),
    ).fetchone()
    if usuario:
        db.execute(
            "UPDATE usuarios SET ativo=? WHERE id=?",
            (0 if usuario["ativo"] else 1, usuario_id),
        )
        db.commit()
    return redirect(url_for("painel_admin"))


@app.route("/admin/anuncio/<int:anuncio_id>/toggle", methods=["POST"])
def admin_toggle_anuncio(anuncio_id):
    if not admin():
        return redirect(url_for("index"))
    db = get_db()
    anuncio_item = db.execute(
        "SELECT ativo, estoque FROM anuncios WHERE id=?",
        (anuncio_id,),
    ).fetchone()
    if anuncio_item:
        if not anuncio_item["ativo"] and anuncio_item["estoque"] <= 0:
            flash("Informe estoque antes de ativar o anuncio.", "erro")
            return redirect(url_for("painel_admin"))
        db.execute(
            "UPDATE anuncios SET ativo=? WHERE id=?",
            (0 if anuncio_item["ativo"] else 1, anuncio_id),
        )
        db.commit()
    return redirect(url_for("painel_admin"))


@app.route("/admin/usuario/<int:usuario_id>/plano", methods=["POST"])
def admin_toggle_plano(usuario_id):
    if not admin():
        return redirect(url_for("index"))
    db = get_db()
    usuario = db.execute(
        "SELECT plano_ativo FROM usuarios WHERE id=?",
        (usuario_id,),
    ).fetchone()
    if usuario:
        novo = 0 if usuario["plano_ativo"] else 1
        expira = (date.today() + timedelta(days=30)).isoformat() if novo else None
        db.execute(
            "UPDATE usuarios SET plano_ativo=?, plano_expira=? WHERE id=?",
            (novo, expira, usuario_id),
        )
        db.commit()
        flash(f"Plano {'ativado' if novo else 'desativado'}.", "ok")
    return redirect(url_for("painel_admin"))


@app.errorhandler(400)
def erro_requisicao_invalida(_error):
    flash("Requisicao invalida. Tente novamente.", "erro")
    return redirect(url_for("index"))


@app.errorhandler(404)
def pagina_nao_encontrada(_error):
    return render_template(
        "erro.html",
        titulo="Pagina nao encontrada",
        mensagem="O link que voce tentou abrir nao existe ou foi removido.",
    ), 404


@app.errorhandler(413)
def arquivo_muito_grande(_error):
    flash("Arquivo muito grande. O limite e de 5 MB.", "erro")
    return redirect(url_for("meus_anuncios"))


@app.errorhandler(500)
def erro_interno(_error):
    return render_template(
        "erro.html",
        titulo="Erro interno",
        mensagem="Ocorreu um erro inesperado. Tente novamente em instantes.",
    ), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = FLASK_ENV != "production"
    print(f"\nMercado Colatina rodando em http://localhost:{port}")
    if debug:
        print("   Admin local padrao: admin / admin123\n")
    else:
        print("   Admin: criado via ADMIN_USERNAME / ADMIN_PASSWORD\n")
    app.run(debug=debug, host=os.environ.get("HOST", "127.0.0.1"), port=port)
