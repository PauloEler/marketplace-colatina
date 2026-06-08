import sqlite3, os
from werkzeug.security import generate_password_hash

DB_PATH = os.environ.get(
    'DATABASE_PATH',
    os.path.join(os.path.dirname(__file__), 'marketplace.db')
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _criar_admin_por_ambiente(db):
    flask_env = os.environ.get('FLASK_ENV', 'development').lower()
    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    admin_nome = os.environ.get('ADMIN_NOME', 'Administrador')
    admin_whatsapp = os.environ.get('ADMIN_WHATSAPP', '')

    if admin_username and admin_password:
        senha_hash = generate_password_hash(admin_password)
        db.execute(
            """
            INSERT OR IGNORE INTO usuarios
                (nome, username, senha, whatsapp, is_admin)
            VALUES (?, ?, ?, ?, 1)
            """,
            (admin_nome, admin_username, senha_hash, admin_whatsapp)
        )
        return

    if flask_env == 'production':
        raise RuntimeError(
            'ADMIN_USERNAME e ADMIN_PASSWORD devem ser configurados em producao.'
        )


def init_db():
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            whatsapp TEXT NOT NULL DEFAULT '',
            is_admin INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            plano_ativo INTEGER DEFAULT 0,
            plano_expira DATE,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS anuncios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            preco TEXT NOT NULL,
            categoria TEXT NOT NULL,
            condicao TEXT NOT NULL DEFAULT 'Usado',
            foto TEXT,
            ativo INTEGER DEFAULT 1,
            destaque INTEGER DEFAULT 0,
            visualizacoes INTEGER DEFAULT 0,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    ''')
    _criar_admin_por_ambiente(db)
    db.commit()
    db.close()
