import os
import sqlite3

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "marketplace.db"))
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

USE_PG = bool(DATABASE_URL)


class Row(dict):
    """Dict que também aceita índice inteiro, como sqlite3.Row."""
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


class _PgCursor:
    def __init__(self, cur):
        self._c = cur

    def _wrap(self, row):
        if row is None:
            return None
        cols = [d[0] for d in self._c.description]
        return Row(zip(cols, row))

    def fetchone(self):
        return self._wrap(self._c.fetchone())

    def fetchall(self):
        return [self._wrap(r) for r in self._c.fetchall()]


class _PgConn:
    def __init__(self, conn):
        self._c = conn

    def execute(self, query, params=()):
        cur = self._c.cursor()
        cur.execute(query.replace("?", "%s"), params)
        return _PgCursor(cur)

    def commit(self):
        self._c.commit()

    def close(self):
        self._c.close()


def get_db():
    if USE_PG:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        return _PgConn(conn)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    if USE_PG:
        _init_pg()
    else:
        _init_sqlite()


def _init_sqlite():
    db = get_db()
    db.executescript(
        """
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
        """
    )
    _seed_admin(db)
    _hash_plain_passwords(db)
    db.commit()
    db.close()


def _init_pg():
    import psycopg2
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            whatsapp TEXT NOT NULL DEFAULT '',
            is_admin INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            plano_ativo INTEGER DEFAULT 0,
            plano_expira DATE,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS anuncios (
            id SERIAL PRIMARY KEY,
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
        )
        """
    )
    _seed_admin(db)
    db.commit()
    db.close()


def _seed_admin(db):
    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    admin_nome = os.environ.get("ADMIN_NAME", "Administrador")
    admin_whatsapp = os.environ.get("ADMIN_WHATSAPP", "27999999999")
    flask_env = os.environ.get("FLASK_ENV", "production")

    existente = db.execute(
        "SELECT id FROM usuarios WHERE username=?", (admin_username,)
    ).fetchone()

    if not existente:
        if admin_password:
            db.execute(
                "INSERT INTO usuarios (nome, username, senha, whatsapp, is_admin) VALUES (?,?,?,?,1)",
                (admin_nome, admin_username, generate_password_hash(admin_password), admin_whatsapp),
            )
        elif flask_env != "production":
            db.execute(
                "INSERT INTO usuarios (nome, username, senha, whatsapp, is_admin) VALUES (?,?,?,?,1)",
                (admin_nome, admin_username, generate_password_hash("admin123"), admin_whatsapp),
            )


def _hash_plain_passwords(db):
    usuarios = db.execute("SELECT id, senha FROM usuarios").fetchall()
    for u in usuarios:
        senha = u["senha"] or ""
        if not senha.startswith("scrypt:") and not senha.startswith("pbkdf2:"):
            db.execute(
                "UPDATE usuarios SET senha=? WHERE id=?",
                (generate_password_hash(senha), u["id"]),
            )
