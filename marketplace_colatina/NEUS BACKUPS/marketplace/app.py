from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from database import init_db, get_db
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'colatina_market_2026')

# Inicializa banco ao subir (necessário no Railway)
with app.app_context():
    init_db()

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

CATEGORIAS = [
    'Eletrônicos', 'Móveis', 'Roupas e Calçados', 'Veículos',
    'Eletrodomésticos', 'Imóveis', 'Serviços', 'Alimentos', 'Outros'
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def usuario_logado():
    return session.get('usuario_id')

def is_admin():
    return session.get('is_admin', False)

# ─── ROTAS PÚBLICAS ─────────────────────────────────────────────────────────

@app.route('/')
def index():
    db = get_db()
    busca = request.args.get('q', '')
    categoria = request.args.get('categoria', '')
    
    query = "SELECT a.*, u.nome as vendedor_nome, u.whatsapp FROM anuncios a JOIN usuarios u ON a.usuario_id = u.id WHERE a.ativo = 1"
    params = []
    
    if busca:
        query += " AND (a.titulo LIKE ? OR a.descricao LIKE ?)"
        params += [f'%{busca}%', f'%{busca}%']
    if categoria:
        query += " AND a.categoria = ?"
        params.append(categoria)
    
    query += " ORDER BY a.criado_em DESC"
    anuncios = db.execute(query, params).fetchall()
    return render_template('index.html', anuncios=anuncios, categorias=CATEGORIAS, busca=busca, categoria_sel=categoria)

@app.route('/anuncio/<int:id>')
def anuncio(id):
    db = get_db()
    a = db.execute(
        "SELECT a.*, u.nome as vendedor_nome, u.whatsapp FROM anuncios a JOIN usuarios u ON a.usuario_id = u.id WHERE a.id = ? AND a.ativo = 1",
        (id,)
    ).fetchone()
    if not a:
        flash('Anúncio não encontrado.', 'erro')
        return redirect(url_for('index'))
    
    db.execute("UPDATE anuncios SET visualizacoes = visualizacoes + 1 WHERE id = ?", (id,))
    db.commit()
    return render_template('anuncio.html', a=a)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ─── LOGIN / LOGOUT ──────────────────────────────────────────────────────────

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        username = request.form['username'].strip()
        senha = request.form['senha'].strip()
        whatsapp = request.form['whatsapp'].strip()
        db = get_db()
        try:
            db.execute("INSERT INTO usuarios (nome, username, senha, whatsapp) VALUES (?,?,?,?)",
                       (nome, username, senha, whatsapp))
            db.commit()
            flash('Cadastro realizado! Faça login.', 'ok')
            return redirect(url_for('login'))
        except:
            flash('Este username já está em uso. Escolha outro.', 'erro')
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        senha = request.form['senha'].strip()
        db = get_db()
        u = db.execute("SELECT * FROM usuarios WHERE username = ? AND senha = ? AND ativo = 1", (username, senha)).fetchone()
        if u:
            session['usuario_id'] = u['id']
            session['usuario_nome'] = u['nome']
            session['is_admin'] = bool(u['is_admin'])
            flash(f'Bem-vindo, {u["nome"]}!', 'ok')
            return redirect(url_for('index'))
        flash('Usuário ou senha incorretos.', 'erro')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ─── ANÚNCIOS ────────────────────────────────────────────────────────────────

@app.route('/criar', methods=['GET', 'POST'])
def criar_anuncio():
    if not usuario_logado():
        flash('Faça login para anunciar.', 'erro')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        titulo = request.form['titulo'].strip()
        descricao = request.form['descricao'].strip()
        preco = request.form['preco'].strip()
        categoria = request.form['categoria']
        condicao = request.form['condicao']
        
        foto = None
        if 'foto' in request.files:
            f = request.files['foto']
            if f and f.filename and allowed_file(f.filename):
                ext = f.filename.rsplit('.', 1)[1].lower()
                foto = f"{uuid.uuid4().hex}.{ext}"
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], foto))
        
        db = get_db()
        db.execute(
            "INSERT INTO anuncios (usuario_id, titulo, descricao, preco, categoria, condicao, foto) VALUES (?,?,?,?,?,?,?)",
            (session['usuario_id'], titulo, descricao, preco, categoria, condicao, foto)
        )
        db.commit()
        flash('Anúncio criado! Aguarde aprovação se necessário.', 'ok')
        return redirect(url_for('meus_anuncios'))
    
    return render_template('criar.html', categorias=CATEGORIAS)

@app.route('/meus-anuncios')
def meus_anuncios():
    if not usuario_logado():
        return redirect(url_for('login'))
    db = get_db()
    anuncios = db.execute(
        "SELECT * FROM anuncios WHERE usuario_id = ? ORDER BY criado_em DESC",
        (session['usuario_id'],)
    ).fetchall()
    return render_template('meus_anuncios.html', anuncios=anuncios)

@app.route('/minha-conta', methods=['GET', 'POST'])
def minha_conta():
    if not usuario_logado():
        return redirect(url_for('login'))
    if request.method == 'POST':
        senha_atual = request.form['senha_atual'].strip()
        nova_senha = request.form['nova_senha'].strip()
        confirmar = request.form['confirmar'].strip()
        db = get_db()
        u = db.execute("SELECT * FROM usuarios WHERE id = ?", (session['usuario_id'],)).fetchone()
        if u['senha'] != senha_atual:
            flash('Senha atual incorreta.', 'erro')
        elif nova_senha != confirmar:
            flash('Nova senha e confirmação não coincidem.', 'erro')
        elif len(nova_senha) < 4:
            flash('Senha muito curta. Mínimo 4 caracteres.', 'erro')
        else:
            db.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (nova_senha, session['usuario_id']))
            db.commit()
            flash('Senha alterada com sucesso!', 'ok')
    return render_template('minha_conta.html')

@app.route('/deletar/<int:id>', methods=['POST'])
def deletar_anuncio(id):
    if not usuario_logado():
        return redirect(url_for('login'))
    db = get_db()
    a = db.execute("SELECT * FROM anuncios WHERE id = ? AND usuario_id = ?", (id, session['usuario_id'])).fetchone()
    if a or is_admin():
        db.execute("UPDATE anuncios SET ativo = 0 WHERE id = ?", (id,))
        db.commit()
        flash('Anúncio removido.', 'ok')
    return redirect(url_for('meus_anuncios'))

# ─── ADMIN ───────────────────────────────────────────────────────────────────

@app.route('/admin')
def admin():
    if not is_admin():
        return redirect(url_for('index'))
    db = get_db()
    usuarios = db.execute("SELECT * FROM usuarios ORDER BY criado_em DESC").fetchall()
    anuncios = db.execute("SELECT a.*, u.nome as vendedor_nome FROM anuncios a JOIN usuarios u ON a.usuario_id = u.id ORDER BY a.criado_em DESC").fetchall()
    return render_template('admin.html', usuarios=usuarios, anuncios=anuncios)

@app.route('/admin/usuario', methods=['POST'])
def admin_criar_usuario():
    if not is_admin():
        return redirect(url_for('index'))
    nome = request.form['nome'].strip()
    username = request.form['username'].strip()
    senha = request.form['senha'].strip()
    whatsapp = request.form['whatsapp'].strip()
    is_adm = 1 if request.form.get('is_admin') else 0
    db = get_db()
    try:
        db.execute("INSERT INTO usuarios (nome, username, senha, whatsapp, is_admin) VALUES (?,?,?,?,?)",
                   (nome, username, senha, whatsapp, is_adm))
        db.commit()
        flash(f'Usuário {nome} cadastrado.', 'ok')
    except:
        flash('Username já existe.', 'erro')
    return redirect(url_for('admin'))

@app.route('/admin/usuario/<int:id>/toggle', methods=['POST'])
def admin_toggle_usuario(id):
    if not is_admin():
        return redirect(url_for('index'))
    db = get_db()
    u = db.execute("SELECT ativo FROM usuarios WHERE id = ?", (id,)).fetchone()
    if u:
        db.execute("UPDATE usuarios SET ativo = ? WHERE id = ?", (0 if u['ativo'] else 1, id))
        db.commit()
    return redirect(url_for('admin'))

@app.route('/admin/anuncio/<int:id>/toggle', methods=['POST'])
def admin_toggle_anuncio(id):
    if not is_admin():
        return redirect(url_for('index'))
    db = get_db()
    a = db.execute("SELECT ativo FROM anuncios WHERE id = ?", (id,)).fetchone()
    if a:
        db.execute("UPDATE anuncios SET ativo = ? WHERE id = ?", (0 if a['ativo'] else 1, id))
        db.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print("\n✅ Marketplace Colatina rodando!")
    print(f"   Acesse: http://localhost:{port}")
    print("   Admin:  /admin  |  Login: admin / admin123\n")
    app.run(debug=debug, host='0.0.0.0', port=port)
