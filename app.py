import os
import re
import secrets
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import quote

from flask import Flask, Response, abort, flash, redirect, render_template, request, send_from_directory, session, url_for
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

from database import close_db, get_db, init_db
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
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,24}$")


def limpar_whatsapp(valor):
    return re.sub(r"\D", "", valor or "")


def categoria_label(valor):
    return CATEGORIA_CANONICA.get(valor, valor)


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
    if request.method == "POST":
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
    session.clear()
    return redirect(url_for("index"))


@app.route("/minha-conta", methods=["GET", "POST"])
def minha_conta():
    if not logado():
        return redirect(url_for("login"))

    if request.method == "POST":
        atual = request.form["senha_atual"].strip()
        nova = request.form["nova_senha"].strip()
        confirma = request.form["confirmar"].strip()
        db = get_db()
        usuario = db.execute(
            "SELECT * FROM usuarios WHERE id=?",
            (session["usuario_id"],),
        ).fetchone()

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

    return render_template("minha_conta.html")


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
            ("Dados utilizados", "Nome, nome de usuário, senha protegida, WhatsApp e informações dos anúncios publicados."),
            ("Finalidade", "Os dados são usados para autenticação, administração da conta, publicação dos anúncios e contato entre as partes."),
            ("Proteção", "Senhas não são armazenadas em texto legível. O acesso administrativo deve ser restrito e monitorado."),
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
            ("Negociação entre usuários", "Pagamento, entrega, garantia e demais condições são combinados diretamente entre comprador e vendedor."),
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
    return render_template(
        "admin.html", usuarios=usuarios, anuncios=anuncios, pagamentos=pagamentos
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
