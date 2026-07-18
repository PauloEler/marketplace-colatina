import os
import sqlite3

from flask import g, has_app_context
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "marketplace.db"))
DATABASE_URL = (
    os.environ.get("RESTORED_DATABASE_URL", "").strip()
    or os.environ.get("DATABASE_URL", "").strip()
)
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

    @property
    def rowcount(self):
        return self._c.rowcount


class _PgConn:
    def __init__(self, conn):
        self._c = conn

    def execute(self, query, params=()):
        cur = self._c.cursor()
        cur.execute(query.replace("?", "%s"), params)
        return _PgCursor(cur)

    def commit(self):
        self._c.commit()

    def rollback(self):
        self._c.rollback()

    def close(self):
        self._c.close()


def _abrir_conexao():
    if USE_PG:
        import psycopg2

        conn = psycopg2.connect(DATABASE_URL)
        return _PgConn(conn)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    if not has_app_context():
        return _abrir_conexao()
    if "database_connection" not in g:
        g.database_connection = _abrir_conexao()
    return g.database_connection


def close_db(_error=None):
    if not has_app_context():
        return
    db = g.pop("database_connection", None)
    if db is not None:
        db.close()


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
            termos_aceitos_em TIMESTAMP,
            loja_nome TEXT,
            loja_descricao TEXT NOT NULL DEFAULT '',
            loja_bairro TEXT NOT NULL DEFAULT '',
            loja_whatsapp TEXT NOT NULL DEFAULT '',
            ultimo_acesso_em TIMESTAMP,
            loja_verificada INTEGER NOT NULL DEFAULT 0,
            fundador INTEGER NOT NULL DEFAULT 0,
            fundador_desde TIMESTAMP,
            fundador_origem TEXT,
            fundador_removido_em TIMESTAMP,
            fundador_alterado_por INTEGER,
            fundador_beneficios TEXT NOT NULL DEFAULT '{}',
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
            bairro TEXT NOT NULL DEFAULT '',
            foto TEXT,
            foto_id TEXT,
            ativo INTEGER DEFAULT 1,
            estoque INTEGER NOT NULL DEFAULT 1,
            destaque INTEGER DEFAULT 0,
            visualizacoes INTEGER DEFAULT 0,
            contatos_whatsapp INTEGER DEFAULT 0,
            excluido_em TIMESTAMP,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            valor TEXT NOT NULL,
            metodo TEXT NOT NULL DEFAULT 'PIX',
            status TEXT NOT NULL DEFAULT 'pendente',
            referencia TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
        CREATE INDEX IF NOT EXISTS idx_pagamentos_usuario_status
            ON pagamentos(usuario_id, status);
        CREATE TABLE IF NOT EXISTS estatisticas (
            chave TEXT PRIMARY KEY,
            valor INTEGER NOT NULL DEFAULT 0
        );
        INSERT OR IGNORE INTO estatisticas (chave, valor)
            VALUES ('acessos_site', 0);
        CREATE TABLE IF NOT EXISTS afiliado_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parceiro TEXT NOT NULL,
            oferta_id TEXT NOT NULL,
            categoria TEXT NOT NULL,
            tipo_evento TEXT NOT NULL,
            origem TEXT NOT NULL DEFAULT 'home',
            dispositivo TEXT NOT NULL,
            ocorrido_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_afiliado_eventos_periodo
            ON afiliado_eventos(tipo_evento, ocorrido_em);
        CREATE INDEX IF NOT EXISTS idx_afiliado_eventos_oferta
            ON afiliado_eventos(oferta_id, tipo_evento, ocorrido_em);
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anuncio_id INTEGER NOT NULL,
            comprador_id INTEGER NOT NULL,
            vendedor_id INTEGER NOT NULL,
            valor TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'aguardando',
            entrega TEXT NOT NULL DEFAULT 'retirada',
            observacao TEXT NOT NULL DEFAULT '',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (anuncio_id) REFERENCES anuncios(id),
            FOREIGN KEY (comprador_id) REFERENCES usuarios(id),
            FOREIGN KEY (vendedor_id) REFERENCES usuarios(id)
        );
        CREATE INDEX IF NOT EXISTS idx_pedidos_comprador
            ON pedidos(comprador_id, criado_em);
        CREATE INDEX IF NOT EXISTS idx_pedidos_vendedor
            ON pedidos(vendedor_id, criado_em);
        CREATE INDEX IF NOT EXISTS idx_pedidos_anuncio_status
            ON pedidos(anuncio_id, status);
        CREATE TABLE IF NOT EXISTS pedido_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            usuario_id INTEGER,
            papel_usuario TEXT NOT NULL,
            descricao TEXT NOT NULL,
            dados_adicionais TEXT NOT NULL DEFAULT '{}',
            estado_anterior TEXT,
            estado_posterior TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            UNIQUE (pedido_id, tipo)
        );
        CREATE INDEX IF NOT EXISTS idx_pedido_eventos_pedido_data
            ON pedido_eventos(pedido_id, criado_em, id);
        CREATE TABLE IF NOT EXISTS denuncias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anuncio_id INTEGER NOT NULL,
            denunciante_id INTEGER NOT NULL,
            motivo TEXT NOT NULL,
            detalhes TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pendente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolvido_em TIMESTAMP,
            resolvido_por INTEGER,
            FOREIGN KEY (anuncio_id) REFERENCES anuncios(id),
            FOREIGN KEY (denunciante_id) REFERENCES usuarios(id),
            FOREIGN KEY (resolvido_por) REFERENCES usuarios(id)
        );
        CREATE INDEX IF NOT EXISTS idx_denuncias_status_criado
            ON denuncias(status, criado_em);
        CREATE INDEX IF NOT EXISTS idx_denuncias_anuncio
            ON denuncias(anuncio_id, status);
        CREATE TABLE IF NOT EXISTS anuncio_fotos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anuncio_id INTEGER NOT NULL,
            foto TEXT NOT NULL,
            foto_id TEXT,
            ordem INTEGER NOT NULL DEFAULT 0,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (anuncio_id) REFERENCES anuncios(id)
        );
        CREATE INDEX IF NOT EXISTS idx_anuncio_fotos_ordem
            ON anuncio_fotos(anuncio_id, ordem);
        CREATE TABLE IF NOT EXISTS tentativas_login (
            chave TEXT PRIMARY KEY,
            falhas INTEGER NOT NULL DEFAULT 0,
            janela_inicio INTEGER NOT NULL,
            bloqueado_ate INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS comunicados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            mensagem TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'informacao',
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_por INTEGER NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            desativado_em TIMESTAMP,
            FOREIGN KEY (criado_por) REFERENCES usuarios(id)
        );
        CREATE INDEX IF NOT EXISTS idx_comunicados_ativo_criado
            ON comunicados(ativo, criado_em);
        CREATE TABLE IF NOT EXISTS loja_administradores (
            administrador_id INTEGER NOT NULL,
            loja_id INTEGER NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (administrador_id, loja_id),
            FOREIGN KEY (administrador_id) REFERENCES usuarios(id),
            FOREIGN KEY (loja_id) REFERENCES usuarios(id)
        );
        CREATE INDEX IF NOT EXISTS idx_loja_administradores_loja
            ON loja_administradores(loja_id);
        """
    )
    colunas = {
        linha[1] for linha in db.execute("PRAGMA table_info(anuncios)").fetchall()
    }
    if "foto_id" not in colunas:
        db.execute("ALTER TABLE anuncios ADD COLUMN foto_id TEXT")
    if "bairro" not in colunas:
        db.execute("ALTER TABLE anuncios ADD COLUMN bairro TEXT NOT NULL DEFAULT ''")
    if "contatos_whatsapp" not in colunas:
        db.execute(
            "ALTER TABLE anuncios ADD COLUMN contatos_whatsapp INTEGER DEFAULT 0"
        )
    if "estoque" not in colunas:
        db.execute("ALTER TABLE anuncios ADD COLUMN estoque INTEGER NOT NULL DEFAULT 1")
    if "excluido_em" not in colunas:
        db.execute("ALTER TABLE anuncios ADD COLUMN excluido_em TIMESTAMP")
    db.execute(
        "INSERT INTO anuncio_fotos (anuncio_id, foto, foto_id, ordem) "
        "SELECT a.id, a.foto, a.foto_id, 0 FROM anuncios a "
        "WHERE a.foto IS NOT NULL AND a.foto<>'' AND NOT EXISTS "
        "(SELECT 1 FROM anuncio_fotos f WHERE f.anuncio_id=a.id)"
    )
    colunas_usuarios = {
        linha[1] for linha in db.execute("PRAGMA table_info(usuarios)").fetchall()
    }
    novas_colunas_usuarios = {
        "termos_aceitos_em": "TIMESTAMP",
        "mp_access_token": "TEXT",
        "mp_refresh_token": "TEXT",
        "mp_user_id": "TEXT",
        "mp_token_expira": "TIMESTAMP",
        "mp_conectado_em": "TIMESTAMP",
        "loja_nome": "TEXT",
        "loja_descricao": "TEXT NOT NULL DEFAULT ''",
        "loja_bairro": "TEXT NOT NULL DEFAULT ''",
        "loja_whatsapp": "TEXT NOT NULL DEFAULT ''",
        "ultimo_acesso_em": "TIMESTAMP",
        "loja_verificada": "INTEGER NOT NULL DEFAULT 0",
        "fundador": "INTEGER NOT NULL DEFAULT 0",
        "fundador_desde": "TIMESTAMP",
        "fundador_origem": "TEXT",
        "fundador_removido_em": "TIMESTAMP",
        "fundador_alterado_por": "INTEGER",
        "fundador_beneficios": "TEXT NOT NULL DEFAULT '{}'",
    }
    for nome, tipo in novas_colunas_usuarios.items():
        if nome not in colunas_usuarios:
            db.execute(f"ALTER TABLE usuarios ADD COLUMN {nome} {tipo}")
    db.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_loja_nome "
        "ON usuarios(lower(loja_nome)) "
        "WHERE loja_nome IS NOT NULL AND loja_nome<>''"
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_usuarios_fundador "
        "ON usuarios(fundador, fundador_origem, criado_em)"
    )
    colunas_pedidos = {
        linha[1] for linha in db.execute("PRAGMA table_info(pedidos)").fetchall()
    }
    novas_colunas_pedidos = {
        "pagamento_status": "TEXT NOT NULL DEFAULT 'nao_iniciado'",
        "mp_preference_id": "TEXT",
        "mp_payment_id": "TEXT",
        "mp_checkout_url": "TEXT",
        "comissao": "TEXT NOT NULL DEFAULT '0.00'",
        "admin_email_status": "TEXT NOT NULL DEFAULT 'pendente'",
        "admin_email_enviado_em": "TIMESTAMP",
        "vendedor_confirmou_em": "TIMESTAMP",
        "comprador_confirmou_em": "TIMESTAMP",
        "problema_motivo": "TEXT",
        "problema_descricao": "TEXT",
        "problema_relator_id": "INTEGER",
        "problema_relator_papel": "TEXT",
        "problema_relatado_em": "TIMESTAMP",
    }
    for nome, tipo in novas_colunas_pedidos.items():
        if nome not in colunas_pedidos:
            db.execute(f"ALTER TABLE pedidos ADD COLUMN {nome} {tipo}")
    db.execute(
        "INSERT OR IGNORE INTO pedido_eventos "
        "(pedido_id, tipo, usuario_id, papel_usuario, descricao, dados_adicionais, "
        "estado_anterior, estado_posterior, criado_em) "
        "SELECT p.id, 'PEDIDO_CRIADO', NULL, 'sistema', "
        "'Pedido existente incorporado ao histórico', '{\"legado\":true}', "
        "NULL, p.status, p.criado_em FROM pedidos p"
    )
    _seed_admin(db)
    _seed_loja_administradores(db)
    _backfill_fundadores(db)
    _hash_plain_passwords(db)
    db.commit()
    db.close()


def _init_pg():
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
            termos_aceitos_em TIMESTAMP,
            loja_nome TEXT,
            loja_descricao TEXT NOT NULL DEFAULT '',
            loja_bairro TEXT NOT NULL DEFAULT '',
            loja_whatsapp TEXT NOT NULL DEFAULT '',
            ultimo_acesso_em TIMESTAMP,
            loja_verificada INTEGER NOT NULL DEFAULT 0,
            fundador INTEGER NOT NULL DEFAULT 0,
            fundador_desde TIMESTAMP,
            fundador_origem TEXT,
            fundador_removido_em TIMESTAMP,
            fundador_alterado_por INTEGER,
            fundador_beneficios TEXT NOT NULL DEFAULT '{}',
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
            bairro TEXT NOT NULL DEFAULT '',
            foto TEXT,
            foto_id TEXT,
            ativo INTEGER DEFAULT 1,
            estoque INTEGER NOT NULL DEFAULT 1,
            destaque INTEGER DEFAULT 0,
            visualizacoes INTEGER DEFAULT 0,
            contatos_whatsapp INTEGER DEFAULT 0,
            excluido_em TIMESTAMP,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
        """
    )
    db.execute("ALTER TABLE anuncios ADD COLUMN IF NOT EXISTS foto_id TEXT")
    db.execute(
        "ALTER TABLE anuncios ADD COLUMN IF NOT EXISTS bairro TEXT NOT NULL DEFAULT ''"
    )
    db.execute(
        "ALTER TABLE anuncios ADD COLUMN IF NOT EXISTS contatos_whatsapp INTEGER DEFAULT 0"
    )
    db.execute(
        "ALTER TABLE anuncios ADD COLUMN IF NOT EXISTS estoque INTEGER NOT NULL DEFAULT 1"
    )
    db.execute("ALTER TABLE anuncios ADD COLUMN IF NOT EXISTS excluido_em TIMESTAMP")
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS pagamentos (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            valor TEXT NOT NULL,
            metodo TEXT NOT NULL DEFAULT 'PIX',
            status TEXT NOT NULL DEFAULT 'pendente',
            referencia TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
        """
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_pagamentos_usuario_status ON pagamentos(usuario_id, status)"
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS estatisticas (
            chave TEXT PRIMARY KEY,
            valor INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    db.execute(
        "INSERT INTO estatisticas (chave, valor) VALUES (?, ?) ON CONFLICT (chave) DO NOTHING",
        ("acessos_site", 0),
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS afiliado_eventos (
            id SERIAL PRIMARY KEY,
            parceiro TEXT NOT NULL,
            oferta_id TEXT NOT NULL,
            categoria TEXT NOT NULL,
            tipo_evento TEXT NOT NULL,
            origem TEXT NOT NULL DEFAULT 'home',
            dispositivo TEXT NOT NULL,
            ocorrido_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_afiliado_eventos_periodo "
        "ON afiliado_eventos(tipo_evento, ocorrido_em)"
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_afiliado_eventos_oferta "
        "ON afiliado_eventos(oferta_id, tipo_evento, ocorrido_em)"
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            anuncio_id INTEGER NOT NULL,
            comprador_id INTEGER NOT NULL,
            vendedor_id INTEGER NOT NULL,
            valor TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'aguardando',
            entrega TEXT NOT NULL DEFAULT 'retirada',
            observacao TEXT NOT NULL DEFAULT '',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (anuncio_id) REFERENCES anuncios(id),
            FOREIGN KEY (comprador_id) REFERENCES usuarios(id),
            FOREIGN KEY (vendedor_id) REFERENCES usuarios(id)
        )
        """
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_pedidos_comprador ON pedidos(comprador_id, criado_em)"
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_pedidos_vendedor ON pedidos(vendedor_id, criado_em)"
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_pedidos_anuncio_status ON pedidos(anuncio_id, status)"
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS pedido_eventos (
            id SERIAL PRIMARY KEY,
            pedido_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            usuario_id INTEGER,
            papel_usuario TEXT NOT NULL,
            descricao TEXT NOT NULL,
            dados_adicionais TEXT NOT NULL DEFAULT '{}',
            estado_anterior TEXT,
            estado_posterior TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            UNIQUE (pedido_id, tipo)
        )
        """
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_pedido_eventos_pedido_data "
        "ON pedido_eventos(pedido_id, criado_em, id)"
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS denuncias (
            id SERIAL PRIMARY KEY,
            anuncio_id INTEGER NOT NULL,
            denunciante_id INTEGER NOT NULL,
            motivo TEXT NOT NULL,
            detalhes TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pendente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolvido_em TIMESTAMP,
            resolvido_por INTEGER,
            FOREIGN KEY (anuncio_id) REFERENCES anuncios(id),
            FOREIGN KEY (denunciante_id) REFERENCES usuarios(id),
            FOREIGN KEY (resolvido_por) REFERENCES usuarios(id)
        )
        """
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_denuncias_status_criado ON denuncias(status, criado_em)"
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_denuncias_anuncio ON denuncias(anuncio_id, status)"
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS anuncio_fotos (
            id SERIAL PRIMARY KEY,
            anuncio_id INTEGER NOT NULL,
            foto TEXT NOT NULL,
            foto_id TEXT,
            ordem INTEGER NOT NULL DEFAULT 0,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (anuncio_id) REFERENCES anuncios(id)
        )
        """
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_anuncio_fotos_ordem ON anuncio_fotos(anuncio_id, ordem)"
    )
    db.execute(
        "INSERT INTO anuncio_fotos (anuncio_id, foto, foto_id, ordem) "
        "SELECT a.id, a.foto, a.foto_id, 0 FROM anuncios a "
        "WHERE a.foto IS NOT NULL AND a.foto<>'' AND NOT EXISTS "
        "(SELECT 1 FROM anuncio_fotos f WHERE f.anuncio_id=a.id)"
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS tentativas_login (
            chave TEXT PRIMARY KEY,
            falhas INTEGER NOT NULL DEFAULT 0,
            janela_inicio BIGINT NOT NULL,
            bloqueado_ate BIGINT NOT NULL DEFAULT 0
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS comunicados (
            id SERIAL PRIMARY KEY,
            titulo TEXT NOT NULL,
            mensagem TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'informacao',
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_por INTEGER NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            desativado_em TIMESTAMP,
            FOREIGN KEY (criado_por) REFERENCES usuarios(id)
        )
        """
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_comunicados_ativo_criado ON comunicados(ativo, criado_em)"
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS loja_administradores (
            administrador_id INTEGER NOT NULL,
            loja_id INTEGER NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (administrador_id, loja_id),
            FOREIGN KEY (administrador_id) REFERENCES usuarios(id),
            FOREIGN KEY (loja_id) REFERENCES usuarios(id)
        )
        """
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_loja_administradores_loja "
        "ON loja_administradores(loja_id)"
    )
    for coluna, tipo in {
        "termos_aceitos_em": "TIMESTAMP",
        "mp_access_token": "TEXT",
        "mp_refresh_token": "TEXT",
        "mp_user_id": "TEXT",
        "mp_token_expira": "TIMESTAMP",
        "mp_conectado_em": "TIMESTAMP",
        "loja_nome": "TEXT",
        "loja_descricao": "TEXT NOT NULL DEFAULT ''",
        "loja_bairro": "TEXT NOT NULL DEFAULT ''",
        "loja_whatsapp": "TEXT NOT NULL DEFAULT ''",
        "ultimo_acesso_em": "TIMESTAMP",
        "loja_verificada": "INTEGER NOT NULL DEFAULT 0",
        "fundador": "INTEGER NOT NULL DEFAULT 0",
        "fundador_desde": "TIMESTAMP",
        "fundador_origem": "TEXT",
        "fundador_removido_em": "TIMESTAMP",
        "fundador_alterado_por": "INTEGER",
        "fundador_beneficios": "TEXT NOT NULL DEFAULT '{}'",
    }.items():
        db.execute(f"ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS {coluna} {tipo}")
    db.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_loja_nome "
        "ON usuarios(lower(loja_nome)) "
        "WHERE loja_nome IS NOT NULL AND loja_nome<>''"
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_usuarios_fundador "
        "ON usuarios(fundador, fundador_origem, criado_em)"
    )
    for coluna, tipo in {
        "pagamento_status": "TEXT NOT NULL DEFAULT 'nao_iniciado'",
        "mp_preference_id": "TEXT",
        "mp_payment_id": "TEXT",
        "mp_checkout_url": "TEXT",
        "comissao": "TEXT NOT NULL DEFAULT '0.00'",
        "admin_email_status": "TEXT NOT NULL DEFAULT 'pendente'",
        "admin_email_enviado_em": "TIMESTAMP",
        "vendedor_confirmou_em": "TIMESTAMP",
        "comprador_confirmou_em": "TIMESTAMP",
        "problema_motivo": "TEXT",
        "problema_descricao": "TEXT",
        "problema_relator_id": "INTEGER",
        "problema_relator_papel": "TEXT",
        "problema_relatado_em": "TIMESTAMP",
    }.items():
        db.execute(f"ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS {coluna} {tipo}")
    db.execute(
        "INSERT INTO pedido_eventos "
        "(pedido_id, tipo, usuario_id, papel_usuario, descricao, dados_adicionais, "
        "estado_anterior, estado_posterior, criado_em) "
        "SELECT p.id, 'PEDIDO_CRIADO', NULL, 'sistema', "
        "'Pedido existente incorporado ao histórico', '{\"legado\":true}', "
        "NULL, p.status, p.criado_em FROM pedidos p "
        "ON CONFLICT (pedido_id, tipo) DO NOTHING"
    )
    _seed_admin(db)
    _seed_loja_administradores(db)
    _backfill_fundadores(db)
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
                (
                    admin_nome,
                    admin_username,
                    generate_password_hash(admin_password),
                    admin_whatsapp,
                ),
            )
        elif flask_env != "production":
            db.execute(
                "INSERT INTO usuarios (nome, username, senha, whatsapp, is_admin) VALUES (?,?,?,?,1)",
                (
                    admin_nome,
                    admin_username,
                    generate_password_hash("admin123"),
                    admin_whatsapp,
                ),
            )


def _seed_loja_administradores(db):
    """Vincula gestores a lojas sem compartilhar senhas ou fundir cadastros.

    Formato da variavel: gestor:loja,gestor2:loja2. Os dois lados usam o
    username existente. Vinculos incompletos sao ignorados e tentados de novo
    na proxima inicializacao.
    """
    configuracao = os.environ.get(
        "STORE_MANAGER_ASSIGNMENTS",
        "topatudocolatinense:admin,admin:topatudocolatinense",
    ).strip()
    if not configuracao:
        return
    for item in configuracao.split(","):
        gestor_username, separador, loja_username = item.strip().partition(":")
        if not separador or not gestor_username or not loja_username:
            continue
        gestor = db.execute(
            "SELECT id FROM usuarios WHERE lower(username)=lower(?) AND ativo=1",
            (gestor_username,),
        ).fetchone()
        loja = db.execute(
            "SELECT id FROM usuarios WHERE lower(username)=lower(?) AND ativo=1",
            (loja_username,),
        ).fetchone()
        if not gestor or not loja or gestor["id"] == loja["id"]:
            continue
        if USE_PG:
            db.execute(
                "INSERT INTO loja_administradores (administrador_id, loja_id) "
                "VALUES (?, ?) ON CONFLICT (administrador_id, loja_id) DO NOTHING",
                (gestor["id"], loja["id"]),
            )
        else:
            db.execute(
                "INSERT OR IGNORE INTO loja_administradores "
                "(administrador_id, loja_id) VALUES (?, ?)",
                (gestor["id"], loja["id"]),
            )


def _backfill_fundadores(db):
    try:
        limite = int(os.environ.get("FOUNDERS_LIMIT", "100"))
    except ValueError:
        limite = 100
    limite = max(0, min(limite, 10000))
    if not limite:
        return

    total = db.execute(
        "SELECT COUNT(*) FROM usuarios WHERE fundador_origem='automatico'"
    ).fetchone()[0]
    vagas = max(0, limite - total)
    if not vagas:
        return

    candidatos = db.execute(
        "SELECT id FROM usuarios WHERE fundador=0 AND fundador_origem IS NULL "
        "ORDER BY criado_em ASC, id ASC LIMIT ?",
        (vagas,),
    ).fetchall()
    for usuario in candidatos:
        db.execute(
            "UPDATE usuarios SET fundador=1, fundador_desde=COALESCE(criado_em, "
            "CURRENT_TIMESTAMP), fundador_origem='automatico' WHERE id=?",
            (usuario["id"],),
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
