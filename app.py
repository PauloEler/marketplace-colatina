import os
import re
import secrets
import base64
import hashlib
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import quote

from flask import Flask, Response, abort, flash, redirect, render_template, request, send_from_directory, session, url_for
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

from database import close_db, get_db, init_db
from mercadopago_service import (
    MercadoPagoError,
    REDIRECT_URI as MP_REDIRECT_URI,
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
from storage import excluir_imagem, salvar_imagem

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY")
FLASK_ENV = os.environ.get("FLASK_ENV", "production")

if not SECRET_KEY:
    if FLASK_ENV == "production":
        raise RuntimeError("SECRET_KEY precisa estar definida em producao.")
    SECRET_KEY = "dev-secret-key"

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
try:
    MARKETPLACE_FEE_PERCENT = Decimal(
        os.environ.get("MARKETPLACE_FEE_PERCENT", "0")
    )
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


def limpar_whatsapp(valor):
    return re.sub(r"\D", "", valor or "")


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
        return "Username invalido. Use 3 a 24 caracteres com letras, numeros ou underscore."
    if len(senha) < 8:
        return "Use uma senha com pelo menos 8 caracteres."
    whatsapp_limpo = limpar_whatsapp(whatsapp)
    if len(whatsapp_limpo) not in {10, 11}:
        return "WhatsApp invalido. Informe DDD + numero."
    return None


def validar_anuncio(titulo, descricao, preco, categoria, condicao):
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
        return True, f"Voce tem {restam} anuncio(s) gratuito(s) restante(s)."
    return False, "limite"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def logado():
    return session.get("usuario_id")


def admin():
    return session.get("is_admin", False)


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
app.jinja_env.globals["mercadopago_pagamentos_configurados"] = mercadopago_pagamentos_configurados


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
        linha = get_db().execute(
            "SELECT valor FROM estatisticas WHERE chave=?",
            ("acessos_site",),
        ).fetchone()
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
    usuario = get_db().execute(
        "SELECT id, nome, username, is_admin, ativo FROM usuarios WHERE id=?",
        (usuario_id,),
    ).fetchone()
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
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self' data: https://res.cloudinary.com; style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'self'",
    )
    if request.is_secure:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


@app.before_request
def proteger_formularios():
    if request.method == "POST" and request.endpoint != "mercadopago_webhook":
        token_sessao = session.get("_csrf_token")
        token_form = request.form.get("csrf_token")
        if not token_sessao or not token_form or token_sessao != token_form:
            abort(400)


@app.route("/")
def index():
    db = get_db()
    busca = request.args.get("q", "")
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
        query += " AND (a.titulo LIKE ? OR a.descricao LIKE ?)"
        params += [f"%{busca}%", f"%{busca}%"]
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
    conteudo = f"User-agent: *\nAllow: /\nSitemap: {url_for('sitemap', _external=True)}\n"
    return Response(conteudo, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    endpoints = [
        "index",
        "cadastro",
        "login",
        "pagina_seguranca",
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
        flash("Anuncio nao encontrado.", "erro")
        return redirect(url_for("index"))

    if session.get("usuario_id") != anuncio_item["usuario_id"]:
        db.execute(
            "UPDATE anuncios SET visualizacoes = visualizacoes + 1 WHERE id=?",
            (anuncio_id,),
        )
        db.commit()
    return render_template("anuncio.html", a=anuncio_item)


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        username = request.form["username"].strip()
        senha = request.form["senha"].strip()
        whatsapp = limpar_whatsapp(request.form["whatsapp"].strip())
        erro = validar_usuario(nome, username, senha, whatsapp)
        if erro:
            flash(erro, "erro")
            return render_template("cadastro.html")
        db = get_db()
        try:
            db.execute(
                "INSERT INTO usuarios (nome, username, senha, whatsapp) VALUES (?,?,?,?)",
                (nome, username, generate_password_hash(senha), whatsapp),
            )
            db.commit()
            flash("Conta criada! Faca login.", "ok")
            return redirect(url_for("login"))
        except Exception:
            flash("Username ja em uso. Escolha outro.", "erro")
    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        senha = request.form["senha"].strip()
        if not username or not senha:
            flash("Preencha usuario e senha.", "erro")
            return render_template("login.html")
        db = get_db()
        usuario = db.execute(
            "SELECT * FROM usuarios WHERE username=? AND ativo=1",
            (username,),
        ).fetchone()
        if usuario and check_password_hash(usuario["senha"], senha):
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            session["usuario_username"] = usuario["username"]
            session["is_admin"] = bool(usuario["is_admin"])
            flash(f"Bem-vindo, {usuario['nome']}!", "ok")
            return redirect(url_for("index"))
        flash("Usuario ou senha incorretos.", "erro")
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
        atual = request.form["senha_atual"].strip()
        nova = request.form["nova_senha"].strip()
        confirma = request.form["confirmar"].strip()

        if not check_password_hash(usuario["senha"], atual):
            flash("Senha atual incorreta.", "erro")
        elif nova != confirma:
            flash("Nova senha e confirmacao nao coincidem.", "erro")
        elif len(nova) < 8:
            flash("Use uma senha com pelo menos 8 caracteres.", "erro")
        else:
            db.execute(
                "UPDATE usuarios SET senha=? WHERE id=?",
                (generate_password_hash(nova), session["usuario_id"]),
            )
            db.commit()
            flash("Senha alterada com sucesso!", "ok")

    return render_template("minha_conta.html", usuario=usuario)


@app.route("/mercadopago/conectar")
def mercadopago_conectar():
    if not logado():
        return redirect(url_for("login"))
    if not mercadopago_configurado():
        flash("A integracao com o Mercado Pago ainda esta sendo configurada.", "erro")
        return redirect(url_for("minha_conta"))

    state = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
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
        flash("Faca login para anunciar.", "erro")
        return redirect(url_for("login"))

    pode, aviso = pode_criar_anuncio(session["usuario_id"])
    if not pode:
        return redirect(url_for("assinar"))

    if request.method == "POST":
        pode, _ = pode_criar_anuncio(session["usuario_id"])
        if not pode:
            return redirect(url_for("assinar"))

        titulo = request.form["titulo"].strip()
        descricao = request.form["descricao"].strip()
        preco = normalizar_preco(request.form["preco"])
        categoria = request.form["categoria"]
        condicao = request.form["condicao"]
        erro = validar_anuncio(titulo, descricao, preco, categoria, condicao)
        if erro:
            flash(erro, "erro")
            return render_template("criar.html", categorias=CATEGORIAS, aviso=aviso)
        foto = None
        foto_id = None

        if "foto" in request.files:
            arquivo = request.files["foto"]
            if arquivo and arquivo.filename:
                if not allowed_file(arquivo.filename):
                    flash("Formato de imagem invalido. Use JPG, JPEG, PNG ou WEBP.", "erro")
                    return render_template("criar.html", categorias=CATEGORIAS, aviso=aviso)
                extensao = arquivo.filename.rsplit(".", 1)[1].lower()
                if not arquivo_e_imagem_valida(arquivo, extensao):
                    flash("O arquivo enviado não é uma imagem válida.", "erro")
                    return render_template("criar.html", categorias=CATEGORIAS, aviso=aviso)
                try:
                    foto, foto_id = salvar_imagem(
                        arquivo, extensao, app.config["UPLOAD_FOLDER"]
                    )
                except Exception:
                    app.logger.exception("Falha ao armazenar imagem do anúncio")
                    flash("Não foi possível enviar a imagem. Tente novamente.", "erro")
                    return render_template("criar.html", categorias=CATEGORIAS, aviso=aviso)

        db = get_db()
        db.execute(
            "INSERT INTO anuncios (usuario_id, titulo, descricao, preco, categoria, condicao, foto, foto_id) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (session["usuario_id"], titulo, descricao, preco, categoria, condicao, foto, foto_id),
        )
        db.commit()
        flash("Anuncio publicado!", "ok")
        return redirect(url_for("meus_anuncios"))

    return render_template("criar.html", categorias=CATEGORIAS, aviso=aviso)


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

    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        descricao = request.form["descricao"].strip()
        preco = normalizar_preco(request.form["preco"])
        categoria = request.form["categoria"]
        condicao = request.form["condicao"]
        erro = validar_anuncio(titulo, descricao, preco, categoria, condicao)
        if erro:
            flash(erro, "erro")
            return render_template(
                "editar.html", a=anuncio_item, categorias=CATEGORIAS
            )

        foto = anuncio_item["foto"]
        foto_id = anuncio_item["foto_id"]
        foto_antiga = None
        foto_antiga_id = None
        arquivo = request.files.get("foto")
        if arquivo and arquivo.filename:
            if not allowed_file(arquivo.filename):
                flash("Formato de imagem inválido. Use JPG, JPEG, PNG ou WEBP.", "erro")
                return render_template("editar.html", a=anuncio_item, categorias=CATEGORIAS)
            extensao = arquivo.filename.rsplit(".", 1)[1].lower()
            if not arquivo_e_imagem_valida(arquivo, extensao):
                flash("O arquivo enviado não é uma imagem válida.", "erro")
                return render_template("editar.html", a=anuncio_item, categorias=CATEGORIAS)
            foto_antiga = foto
            foto_antiga_id = foto_id
            try:
                foto, foto_id = salvar_imagem(
                    arquivo, extensao, app.config["UPLOAD_FOLDER"]
                )
            except Exception:
                app.logger.exception("Falha ao substituir imagem do anúncio")
                flash("Não foi possível enviar a nova imagem. Tente novamente.", "erro")
                return render_template("editar.html", a=anuncio_item, categorias=CATEGORIAS)

        db.execute(
            "UPDATE anuncios SET titulo=?, descricao=?, preco=?, categoria=?, condicao=?, foto=?, foto_id=? WHERE id=?",
            (titulo, descricao, preco, categoria, condicao, foto, foto_id, anuncio_id),
        )
        db.commit()

        if foto_antiga:
            try:
                excluir_imagem(
                    foto_antiga, foto_antiga_id, app.config["UPLOAD_FOLDER"]
                )
            except Exception:
                app.logger.exception("Falha ao remover imagem antiga do anúncio")

        flash("Anúncio atualizado com sucesso.", "ok")
        return redirect(url_for("meus_anuncios"))

    return render_template("editar.html", a=anuncio_item, categorias=CATEGORIAS)


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
        flash("Este anuncio nao esta mais disponivel.", "erro")
        return redirect(url_for("index"))
    if anuncio_item["usuario_id"] == session["usuario_id"]:
        flash("Voce nao pode comprar o proprio anuncio.", "erro")
        return redirect(url_for("anuncio", anuncio_id=anuncio_id))

    pedido_existente = db.execute(
        "SELECT id FROM pedidos WHERE anuncio_id=? AND comprador_id=? "
        "AND status IN ('aguardando','confirmado') ORDER BY criado_em DESC LIMIT 1",
        (anuncio_id, session["usuario_id"]),
    ).fetchone()
    if pedido_existente:
        flash("Voce ja possui um pedido ativo para este anuncio.", "erro")
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
        flash("Pedido enviado! Aguarde a confirmacao do vendedor.", "ok")
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
        flash("Este pedido nao permite mais essa acao.", "erro")
        return redirect(url_for("pedidos"))
    if acao == "cancelar" and pedido["pagamento_status"] == "aprovado":
        flash("Um pedido pago precisa passar pelo atendimento para ser cancelado.", "erro")
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
        mensagem = "Pedido confirmado e anuncio reservado."
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
            db.execute(
                "UPDATE anuncios SET ativo=1 WHERE id=?",
                (pedido["anuncio_id"],),
            )
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
            "notification_url": url_for(
                "mercadopago_webhook", _external=True
            ),
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
    vendedor = get_db().execute(
        "SELECT id FROM usuarios WHERE mp_user_id=?", (str(mp_user_id),)
    ).fetchone()
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
            ("Converse com clareza", "Confirme o estado do produto, o valor final, a forma de pagamento e o local de entrega antes de fechar o negócio."),
            ("Prefira locais seguros", "Quando possível, encontre a outra pessoa em local público, movimentado e durante o dia. Avise alguém de confiança."),
            ("Proteja seus dados", "Nunca compartilhe senhas, códigos recebidos por mensagem, dados bancários completos ou documentos sem necessidade."),
            ("Desconfie de pressa ou vantagem excessiva", "Preços muito abaixo do mercado, cobranças antecipadas e pedidos para sair dos canais combinados podem indicar fraude."),
        ],
    )


@app.route("/privacidade")
def pagina_privacidade():
    return render_template(
        "pagina_info.html",
        titulo="Privacidade",
        resumo="Tratamos apenas os dados necessários para manter sua conta e permitir o contato entre compradores e vendedores.",
        secoes=[
            ("Dados utilizados", "Nome, nome de usuário, senha protegida, WhatsApp, informações dos anúncios, histórico dos pedidos e situação dos pagamentos realizados."),
            ("Finalidade", "Os dados são usados para autenticação, administração da conta, publicação dos anúncios, organização dos pedidos, contato entre as partes e confirmação dos pagamentos."),
            ("Mercado Pago", "Quando o vendedor conecta sua conta, guardamos de forma criptografada apenas as credenciais técnicas necessárias para processar e conferir pagamentos. Dados de cartão não passam pelo Mercado Colatina."),
            ("Proteção", "Senhas e credenciais de integração não são armazenadas em texto legível. O acesso administrativo deve ser restrito e monitorado."),
            ("Seus direitos", "O titular pode solicitar correção ou exclusão dos seus dados ao administrador do Mercado Colatina."),
        ],
    )


@app.route("/termos")
def pagina_termos():
    return render_template(
        "pagina_info.html",
        titulo="Termos de uso",
        resumo="O Mercado Colatina aproxima compradores e vendedores, mas não participa diretamente das negociações.",
        secoes=[
            ("Responsabilidade do anunciante", "O anunciante deve fornecer informações verdadeiras, manter o anúncio atualizado e possuir legitimidade para vender o item ou serviço."),
            ("Conteúdo proibido", "Não são permitidos produtos ilegais, conteúdo enganoso, ofensivo, perigoso ou que viole direitos de terceiros."),
            ("Pedidos entre usuários", "O pedido registra o interesse de compra e permite que o vendedor confirme a disponibilidade. Entrega, garantia e demais condições devem ser combinadas entre comprador e vendedor."),
            ("Pagamentos", "Quando disponível, o pagamento é processado pelo Mercado Pago diretamente na conta conectada pelo vendedor. Taxas, análises, estornos e contestações seguem também as regras do Mercado Pago. O Mercado Colatina não recebe o valor do produto."),
            ("Moderação", "Anúncios e contas que violem estas regras podem ser ocultados ou desativados para proteger a comunidade."),
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
    if anuncio_item and (anuncio_item["usuario_id"] == session["usuario_id"] or admin()):
        db.execute("UPDATE anuncios SET ativo=0 WHERE id=?", (anuncio_id,))
        db.commit()
        flash("Anuncio removido.", "ok")
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
    return render_template(
        "admin.html",
        usuarios=usuarios,
        anuncios=anuncios,
        pagamentos=pagamentos,
        pedidos=pedidos_admin,
    )


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
    return render_template("erro.html", titulo="Pagina nao encontrada", mensagem="O link que voce tentou abrir nao existe ou foi removido."), 404


@app.errorhandler(413)
def arquivo_muito_grande(_error):
    flash("Arquivo muito grande. O limite e de 5 MB.", "erro")
    return redirect(request.referrer or url_for("criar_anuncio"))


@app.errorhandler(500)
def erro_interno(_error):
    return render_template("erro.html", titulo="Erro interno", mensagem="Ocorreu um erro inesperado. Tente novamente em instantes."), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = FLASK_ENV != "production"
    print(f"\nMercado Colatina rodando em http://localhost:{port}")
    if debug:
        print("   Admin local padrao: admin / admin123\n")
    else:
        print("   Admin: criado via ADMIN_USERNAME / ADMIN_PASSWORD\n")
    app.run(debug=debug, host="0.0.0.0", port=port)
