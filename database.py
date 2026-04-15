import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), 'marketplace.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

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
        INSERT OR IGNORE INTO usuarios (nome, username, senha, whatsapp, is_admin)
        VALUES ('Administrador', 'admin', 'admin123', '27999999999', 1);
    ''')
    db.commit()
    db.close()
