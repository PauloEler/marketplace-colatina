import os
import re
import secrets
import base64
import hashlib
import hmac
import time
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

from database import close_db, get_db, init_db  # noqa: E402
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

LIMITE_GRATIS = 3
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
LOGIN_MAX_FALHAS = 5
LOGIN_JANELA_SEGUNDOS = 15 * 60


def validar_configuracao_producao():
    if FLASK_ENV != "production":
        return
    obrigatorias = (
        "DATABASE_URL",
        "CLOUDINARY_URL",
        "ADMIN_PASSWORD",
        "ADMIN_WHATSAPP",
        "PIX_KEY",
        "SUPPORT_WHATSAPP",
    )
    ausentes = [nome for nome in obrigatorias if not os.environ.get(nome, "").strip()]
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


validar_configuracao_producao()


with app.app_context():
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    init_db()


app.teardown_appcontext(close_db)
app.jinja_env.globals["csrf_token"] = csrf_token
app.jinja_env.globals["categoria_label"] = categoria_label
app.jinja_env.globals["plano_valido"] = plano_valido
app.jinja_env.globals["foto_url"] = foto_url
app.jinja_env.globals["pedido_status_label"] = pedido_status_label
app.jinja_env.globals["pedido_entrega_label"] = pedido_entrega_label
app.jinja_env.globals["pagamento_status_label"] = pagamento_status_label
app.jinja_env.globals["mercadopago_configurado"] = mercadopago_configurado
app.jinja_env.globals["mercadopago_pagamentos_configurados"] = (
    mercadopago_pagamentos_configurados
)
app.jinja_env.globals["neo_configurado"] = neo_configurado


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
        "SELECT a.*, u.nome AS vendedor_nome, u.whatsapp "
        "FROM anuncios a "
        "JOIN usuarios u ON a.usuario_id = u.id "
        "WHERE a.ativo = 1"
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
        categorias=CATEGORIAS,
        busca=busca,
        cat_sel=categoria,
        info_plano=info_plano,
        valor_plano=VALOR_PLANO,
        mercado_livre_afiliado_url=MERCADO_LIVRE_AFILIADO_URL,
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
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    return Response(xml, mimetype="application/xml")


@app.route("/anuncio/<int:anuncio_id>")
def anuncio(anuncio_id):
    db = get_db()
    anuncio_item = db.execute(
        "SELECT a.*, u.nome AS vendedor_nome, u.whatsapp "
        "FROM anuncios a "
        "JOIN usuarios u ON a.usuario_id = u.id "
        "WHERE a.id=? AND a.ativo=1",
        (anuncio_id,),
    ).fetchone()
    if not anuncio_item:
        flash("Anúncio não encontrado.", "erro")
        return redirect(url_for("index"))

    if session.get("usuario_id") != anuncio_item["usuario_id"]:
        db.execute(
            "UPDATE anuncios SET visualizacoes = visualizacoes + 1 WHERE id=?",
            (anuncio_id,),
        )
        db.commit()
    fotos = db.execute(
        "SELECT * FROM anuncio_fotos WHERE anuncio_id=? ORDER BY ordem, id",
        (anuncio_id,),
    ).fetchall()
    return render_template(
        "anuncio.html",
        a=anuncio_item,
        fotos=fotos,
        denuncia_motivos=DENUNCIA_MOTIVOS,
    )


@app.route("/anuncio/<int:anuncio_id>/contato")
def contato_anuncio(anuncio_id):
    db = get_db()
    anuncio_item = db.execute(
        "SELECT a.id, a.titulo, a.usuario_id, u.whatsapp FROM anuncios a "
        "JOIN usuarios u ON u.id=a.usuario_id WHERE a.id=? AND a.ativo=1 AND u.ativo=1",
        (anuncio_id,),
    ).fetchone()
    if not anuncio_item:
        abort(404)
    if session.get("usuario_id") != anuncio_item["usuario_id"]:
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
    if anuncio_item["usuario_id"] == session["usuario_id"]:
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
            db.execute(
                "INSERT INTO usuarios (nome, username, senha, whatsapp, termos_aceitos_em) "
                "VALUES (?,?,?,?,CURRENT_TIMESTAMP)",
                (nome, username, generate_password_hash(senha), whatsapp),
            )
            db.commit()
            flash("Conta criada! Faça login.", "ok")
            return redirect(url_for("login"))
        except Exception:
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
            db.commit()
            visita_registrada = session.get("_visita_registrada")
            session.clear()
            if visita_registrada:
                session["_visita_registrada"] = True
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            session["usuario_username"] = usuario["username"]
            session["is_admin"] = bool(usuario["is_admin"])
            flash(f"Bem-vindo, {usuario['nome']}!", "ok")
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

    return render_template("minha_conta.html", usuario=usuario)


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
        "AND status IN ('aguardando','confirmado') LIMIT 1",
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
        "SELECT id FROM pedidos WHERE vendedor_id=? AND status='confirmado' "
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

    pode, aviso = pode_criar_anuncio(session["usuario_id"])
    if not pode:
        return redirect(url_for("assinar"))
    rascunho_neo = session.pop("_neo_rascunho", {})

    if request.method == "POST":
        pode, _ = pode_criar_anuncio(session["usuario_id"])
        if not pode:
            return redirect(url_for("assinar"))

        titulo = request.form["titulo"].strip()
        descricao = request.form["descricao"].strip()
        preco = normalizar_preco(request.form["preco"])
        categoria = request.form["categoria"]
        condicao = request.form["condicao"]
        bairro = request.form.get("bairro", "").strip()
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
            "INSERT INTO anuncios (usuario_id, titulo, descricao, preco, categoria, condicao, bairro, foto, foto_id) "
            "VALUES (?,?,?,?,?,?,?,?,?) RETURNING id",
            (
                session["usuario_id"],
                titulo,
                descricao,
                preco,
                categoria,
                condicao,
                bairro,
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
        "SELECT * FROM anuncios WHERE id=?",
        (anuncio_id,),
    ).fetchone()
    if not anuncio_item or (
        anuncio_item["usuario_id"] != session["usuario_id"] and not admin()
    ):
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
            "UPDATE anuncios SET titulo=?, descricao=?, preco=?, categoria=?, condicao=?, bairro=?, foto=?, foto_id=? WHERE id=?",
            (
                titulo,
                descricao,
                preco,
                categoria,
                condicao,
                bairro,
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
        "SELECT usuario_id, ativo FROM anuncios WHERE id=?",
        (anuncio_id,),
    ).fetchone()
    if not anuncio_item or (
        anuncio_item["usuario_id"] != session["usuario_id"] and not admin()
    ):
        abort(404)
    novo_status = 0 if anuncio_item["ativo"] else 1
    if novo_status:
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
    anuncios = db.execute(
        "SELECT * FROM anuncios WHERE usuario_id=? ORDER BY criado_em DESC",
        (session["usuario_id"],),
    ).fetchall()
    return render_template("meus_anuncios.html", anuncios=anuncios)


@app.route("/comprar/<int:anuncio_id>", methods=["GET", "POST"])
def comprar(anuncio_id):
    if not logado():
        flash("Entre na sua conta para fazer um pedido.", "erro")
        return redirect(url_for("login"))

    db = get_db()
    anuncio_item = db.execute(
        "SELECT a.*, u.nome AS vendedor_nome, u.whatsapp "
        "FROM anuncios a JOIN usuarios u ON a.usuario_id=u.id "
        "WHERE a.id=? AND a.ativo=1",
        (anuncio_id,),
    ).fetchone()
    if not anuncio_item:
        flash("Este anúncio não está mais disponível.", "erro")
        return redirect(url_for("index"))
    if anuncio_item["usuario_id"] == session["usuario_id"]:
        flash("Você não pode comprar o próprio anúncio.", "erro")
        return redirect(url_for("anuncio", anuncio_id=anuncio_id))

    pedido_existente = db.execute(
        "SELECT id FROM pedidos WHERE anuncio_id=? AND comprador_id=? "
        "AND status IN ('aguardando','confirmado') ORDER BY criado_em DESC LIMIT 1",
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
        (session["usuario_id"],),
    ).fetchall()
    return render_template("pedidos.html", compras=compras, vendas=vendas)


@app.route("/pedido/<int:pedido_id>/<acao>", methods=["POST"])
def atualizar_pedido(pedido_id, acao):
    if not logado():
        return redirect(url_for("login"))
    if acao not in {"confirmar", "recusar", "cancelar", "concluir"}:
        abort(404)

    db = get_db()
    pedido = db.execute("SELECT * FROM pedidos WHERE id=?", (pedido_id,)).fetchone()
    if not pedido:
        abort(404)

    usuario_id = session["usuario_id"]
    e_admin = admin()
    if acao in {"confirmar", "recusar"}:
        autorizado = pedido["vendedor_id"] == usuario_id or e_admin
        status_permitido = pedido["status"] == "aguardando"
    elif acao == "cancelar":
        autorizado = pedido["comprador_id"] == usuario_id or e_admin
        status_permitido = pedido["status"] in {"aguardando", "confirmado"}
    else:
        autorizado = pedido["comprador_id"] == usuario_id or e_admin
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

    if acao == "confirmar":
        db.execute(
            "UPDATE pedidos SET status='confirmado', atualizado_em=CURRENT_TIMESTAMP WHERE id=?",
            (pedido_id,),
        )
        db.execute("UPDATE anuncios SET ativo=0 WHERE id=?", (pedido["anuncio_id"],))
        db.execute(
            "UPDATE pedidos SET status='recusado', atualizado_em=CURRENT_TIMESTAMP "
            "WHERE anuncio_id=? AND id<>? AND status='aguardando'",
            (pedido["anuncio_id"], pedido_id),
        )
        mensagem = "Pedido confirmado e anúncio reservado."
    elif acao == "recusar":
        db.execute(
            "UPDATE pedidos SET status='recusado', atualizado_em=CURRENT_TIMESTAMP WHERE id=?",
            (pedido_id,),
        )
        mensagem = "Pedido recusado."
    elif acao == "cancelar":
        estava_confirmado = pedido["status"] == "confirmado"
        db.execute(
            "UPDATE pedidos SET status='cancelado', atualizado_em=CURRENT_TIMESTAMP WHERE id=?",
            (pedido_id,),
        )
        if estava_confirmado:
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
    else:
        db.execute(
            "UPDATE pedidos SET status='concluido', atualizado_em=CURRENT_TIMESTAMP WHERE id=?",
            (pedido_id,),
        )
        mensagem = "Compra concluida com sucesso."

    db.commit()
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
        "SELECT * FROM anuncios WHERE id=?",
        (anuncio_id,),
    ).fetchone()
    if anuncio_item and (
        anuncio_item["usuario_id"] == session["usuario_id"] or admin()
    ):
        db.execute("UPDATE anuncios SET ativo=0 WHERE id=?", (anuncio_id,))
        db.commit()
        flash("Anúncio removido.", "ok")
    return redirect(url_for("meus_anuncios"))


@app.route("/admin")
def painel_admin():
    if not admin():
        return redirect(url_for("index"))
    db = get_db()
    usuarios = db.execute("SELECT * FROM usuarios ORDER BY criado_em DESC").fetchall()
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
    denuncias = db.execute(
        "SELECT d.*, a.titulo, a.ativo AS anuncio_ativo, "
        "denunciante.nome AS denunciante_nome, vendedor.nome AS vendedor_nome "
        "FROM denuncias d "
        "JOIN anuncios a ON a.id=d.anuncio_id "
        "JOIN usuarios denunciante ON denunciante.id=d.denunciante_id "
        "JOIN usuarios vendedor ON vendedor.id=a.usuario_id "
        "ORDER BY CASE WHEN d.status='pendente' THEN 0 ELSE 1 END, d.criado_em DESC"
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
    }
    return render_template(
        "admin.html",
        usuarios=usuarios,
        anuncios=anuncios,
        pagamentos=pagamentos,
        pedidos=pedidos_admin,
        denuncias=denuncias,
        denuncia_motivos=DENUNCIA_MOTIVOS,
        metricas=metricas,
    )


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
        db.execute(
            "INSERT INTO usuarios (nome, username, senha, whatsapp, is_admin) VALUES (?,?,?,?,?)",
            (nome, username, generate_password_hash(senha), whatsapp, is_admin),
        )
        db.commit()
        flash(f"Usuario {nome} cadastrado.", "ok")
    except Exception:
        flash("Username ja existe.", "erro")
    return redirect(url_for("painel_admin"))


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
        "SELECT ativo FROM anuncios WHERE id=?",
        (anuncio_id,),
    ).fetchone()
    if anuncio_item:
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
