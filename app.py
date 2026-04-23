import os
import re
import secrets
import uuid
from datetime import date, timedelta

from flask import Flask, abort, flash, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db, init_db

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

CATEGORIAS = [
    "Eletronicos",
    "Moveis",
    "Roupas e Calcados",
    "Veiculos",
    "Eletrodomesticos",
    "Imoveis",
    "Servicos",
    "Alimentos",
    "Outros",
]

LIMITE_GRATIS = 3
VALOR_PLANO = "R$ 10,00"
PIX_CHAVE = "27998984840"
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,24}$")


def limpar_whatsapp(valor):
    return re.sub(r"\D", "", valor or "")


def validar_usuario(nome, username, senha, whatsapp):
    if len(nome) < 3:
        return "Informe um nome com pelo menos 3 caracteres."
    if not USERNAME_RE.fullmatch(username):
        return "Username invalido. Use 3 a 24 caracteres com letras, numeros ou underscore."
    if len(senha) < 4:
        return "Senha muito curta (min. 4 caracteres)."
    whatsapp_limpo = limpar_whatsapp(whatsapp)
    if len(whatsapp_limpo) not in {10, 11}:
        return "WhatsApp invalido. Informe DDD + numero."
    return None


def validar_anuncio(titulo, descricao, preco, categoria, condicao):
    if len(titulo) < 4:
        return "Titulo muito curto."
    if len(descricao) < 10:
        return "Descricao muito curta."
    if len(preco) > 20:
        return "Preco invalido."
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
    if usuario["is_admin"] or usuario["plano_ativo"]:
        return True, None

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


app.jinja_env.globals["csrf_token"] = csrf_token


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
        query += " AND a.categoria = ?"
        params.append(categoria)
    query += " ORDER BY a.criado_em DESC"
    anuncios = db.execute(query, params).fetchall()

    info_plano = None
    if session.get("usuario_id"):
        usuario = db.execute(
            "SELECT plano_ativo, is_admin FROM usuarios WHERE id=?",
            (session["usuario_id"],),
        ).fetchone()
        if not usuario["is_admin"] and not usuario["plano_ativo"]:
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
    return {"status": "ok"}, 200


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
            session["is_admin"] = bool(usuario["is_admin"])
            flash(f"Bem-vindo, {usuario['nome']}!", "ok")
            return redirect(url_for("index"))
        flash("Usuario ou senha incorretos.", "erro")
    return render_template("login.html")


@app.route("/logout")
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
        elif len(nova) < 4:
            flash("Senha muito curta (min. 4 caracteres).", "erro")
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
        preco = request.form["preco"].strip()
        categoria = request.form["categoria"]
        condicao = request.form["condicao"]
        erro = validar_anuncio(titulo, descricao, preco, categoria, condicao)
        if erro:
            flash(erro, "erro")
            return render_template("criar.html", categorias=CATEGORIAS, aviso=aviso)
        foto = None

        if "foto" in request.files:
            arquivo = request.files["foto"]
            if arquivo and arquivo.filename:
                if not allowed_file(arquivo.filename):
                    flash("Formato de imagem invalido. Use JPG, JPEG, PNG ou WEBP.", "erro")
                    return render_template("criar.html", categorias=CATEGORIAS, aviso=aviso)
                extensao = arquivo.filename.rsplit(".", 1)[1].lower()
                foto = f"{uuid.uuid4().hex}.{extensao}"
                arquivo.save(os.path.join(app.config["UPLOAD_FOLDER"], foto))

        db = get_db()
        db.execute(
            "INSERT INTO anuncios (usuario_id, titulo, descricao, preco, categoria, condicao, foto) "
            "VALUES (?,?,?,?,?,?,?)",
            (session["usuario_id"], titulo, descricao, preco, categoria, condicao, foto),
        )
        db.commit()
        flash("Anuncio publicado!", "ok")
        return redirect(url_for("meus_anuncios"))

    return render_template("criar.html", categorias=CATEGORIAS, aviso=aviso)


@app.route("/assinar")
def assinar():
    if not logado():
        return redirect(url_for("login"))
    return render_template("assinar.html", valor=VALOR_PLANO, pix=PIX_CHAVE)


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
    return render_template("admin.html", usuarios=usuarios, anuncios=anuncios)


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
