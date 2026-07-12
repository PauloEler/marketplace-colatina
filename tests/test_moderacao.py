import io
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from werkzeug.security import generate_password_hash


TEST_DIR = tempfile.mkdtemp(prefix="mercado-colatina-tests-")
os.environ.pop("DATABASE_URL", None)
os.environ.pop("RESTORED_DATABASE_URL", None)
os.environ["DATABASE_PATH"] = os.path.join(TEST_DIR, "test.db")
os.environ["FLASK_ENV"] = "testing"
os.environ["SECRET_KEY"] = "test-secret-key"

import app as app_module  # noqa: E402
from app import app  # noqa: E402
from database import USE_PG, get_db, init_db  # noqa: E402


if USE_PG:
    raise RuntimeError("Os testes nunca podem usar PostgreSQL ou o banco de produção.")


class ModeracaoTestCase(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_DIR, ignore_errors=True)

    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        with app.app_context():
            db = get_db()
            for tabela in (
                "comunicados",
                "tentativas_login",
                "anuncio_fotos",
                "denuncias",
                "pedido_eventos",
                "pedidos",
                "pagamentos",
                "anuncios",
                "usuarios",
            ):
                db.execute(f"DELETE FROM {tabela}")
            senha = generate_password_hash("senha-segura")
            db.execute(
                "INSERT INTO usuarios (nome, username, senha, whatsapp) VALUES (?,?,?,?)",
                ("Vendedor", "vendedor", senha, "27999999991"),
            )
            db.execute(
                "INSERT INTO usuarios (nome, username, senha, whatsapp) VALUES (?,?,?,?)",
                ("Comprador", "comprador", senha, "27999999992"),
            )
            db.execute(
                "INSERT INTO usuarios (nome, username, senha, whatsapp, is_admin) VALUES (?,?,?,?,1)",
                ("Moderador", "moderador", senha, "27999999993"),
            )
            self.vendedor_id = db.execute(
                "SELECT id FROM usuarios WHERE username='vendedor'"
            ).fetchone()[0]
            self.comprador_id = db.execute(
                "SELECT id FROM usuarios WHERE username='comprador'"
            ).fetchone()[0]
            self.admin_id = db.execute(
                "SELECT id FROM usuarios WHERE username='moderador'"
            ).fetchone()[0]
            db.execute(
                "INSERT INTO anuncios (usuario_id, titulo, descricao, preco, categoria, condicao) "
                "VALUES (?,?,?,?,?,?)",
                (
                    self.vendedor_id,
                    "Bicicleta aro 29",
                    "Bicicleta usada em bom estado",
                    "1.200,00",
                    "Outros",
                    "Usado",
                ),
            )
            self.anuncio_id = db.execute(
                "SELECT id FROM anuncios WHERE titulo='Bicicleta aro 29'"
            ).fetchone()[0]
            db.commit()

    def autenticar_sessao(self, usuario_id, admin=False):
        with self.client.session_transaction() as sessao:
            sessao["usuario_id"] = usuario_id
            sessao["is_admin"] = admin
            sessao["_csrf_token"] = "token-teste"

    def enviar_denuncia(self):
        self.autenticar_sessao(self.comprador_id)
        return self.client.post(
            f"/anuncio/{self.anuncio_id}/denunciar",
            data={
                "csrf_token": "token-teste",
                "motivo": "enganoso",
                "detalhes": "A descricao nao corresponde a foto.",
            },
        )

    def test_usuario_logado_pode_denunciar_anuncio(self):
        resposta = self.enviar_denuncia()
        self.assertEqual(resposta.status_code, 302)
        with app.app_context():
            denuncia = get_db().execute("SELECT * FROM denuncias").fetchone()
            self.assertEqual(denuncia["status"], "pendente")
            self.assertEqual(denuncia["motivo"], "enganoso")

    def test_denuncia_pendente_nao_e_duplicada(self):
        self.enviar_denuncia()
        self.enviar_denuncia()
        with app.app_context():
            total = get_db().execute("SELECT COUNT(*) FROM denuncias").fetchone()[0]
            self.assertEqual(total, 1)

    def test_dono_nao_pode_denunciar_proprio_anuncio(self):
        self.autenticar_sessao(self.vendedor_id)
        self.client.post(
            f"/anuncio/{self.anuncio_id}/denunciar",
            data={"csrf_token": "token-teste", "motivo": "outro"},
        )
        with app.app_context():
            total = get_db().execute("SELECT COUNT(*) FROM denuncias").fetchone()[0]
            self.assertEqual(total, 0)

    def test_moderador_pode_ocultar_anuncio_denunciado(self):
        self.enviar_denuncia()
        with app.app_context():
            denuncia_id = get_db().execute("SELECT id FROM denuncias").fetchone()[0]
        self.autenticar_sessao(self.admin_id, admin=True)
        resposta = self.client.post(
            f"/admin/denuncia/{denuncia_id}/ocultar",
            data={"csrf_token": "token-teste"},
        )
        self.assertEqual(resposta.status_code, 302)
        with app.app_context():
            db = get_db()
            denuncia = db.execute(
                "SELECT status, resolvido_por FROM denuncias WHERE id=?", (denuncia_id,)
            ).fetchone()
            anuncio = db.execute(
                "SELECT ativo FROM anuncios WHERE id=?", (self.anuncio_id,)
            ).fetchone()
            self.assertEqual(denuncia["status"], "resolvida")
            self.assertEqual(denuncia["resolvido_por"], self.admin_id)
            self.assertEqual(anuncio["ativo"], 0)

    def test_moderador_pode_descartar_denuncia(self):
        self.enviar_denuncia()
        with app.app_context():
            denuncia_id = get_db().execute("SELECT id FROM denuncias").fetchone()[0]
        self.autenticar_sessao(self.admin_id, admin=True)
        self.client.post(
            f"/admin/denuncia/{denuncia_id}/descartar",
            data={"csrf_token": "token-teste"},
        )
        with app.app_context():
            db = get_db()
            status = db.execute(
                "SELECT status FROM denuncias WHERE id=?", (denuncia_id,)
            ).fetchone()[0]
            ativo = db.execute(
                "SELECT ativo FROM anuncios WHERE id=?", (self.anuncio_id,)
            ).fetchone()[0]
            self.assertEqual(status, "descartada")
            self.assertEqual(ativo, 1)

    def test_paginas_de_anuncio_e_moderacao_renderizam(self):
        self.autenticar_sessao(self.comprador_id)
        pagina_anuncio = self.client.get(f"/anuncio/{self.anuncio_id}")
        self.assertEqual(pagina_anuncio.status_code, 200)
        self.assertIn(b"report-card", pagina_anuncio.data)

        self.enviar_denuncia()
        self.autenticar_sessao(self.admin_id, admin=True)
        painel = self.client.get("/admin")
        self.assertEqual(painel.status_code, 200)
        self.assertIn(b"admin-section-heading", painel.data)

    def test_cadastro_exige_e_registra_aceite_dos_termos(self):
        with self.client.session_transaction() as sessao:
            sessao["_csrf_token"] = "token-teste"
        dados = {
            "csrf_token": "token-teste",
            "nome": "Nova Pessoa",
            "username": "nova_pessoa",
            "senha": "senha-segura",
            "whatsapp": "27999999994",
        }
        sem_aceite = self.client.post("/cadastro", data=dados)
        self.assertEqual(sem_aceite.status_code, 200)
        with app.app_context():
            inexistente = (
                get_db()
                .execute("SELECT id FROM usuarios WHERE username='nova_pessoa'")
                .fetchone()
            )
            self.assertIsNone(inexistente)

        dados["aceite_termos"] = "1"
        com_aceite = self.client.post("/cadastro", data=dados)
        self.assertEqual(com_aceite.status_code, 302)
        with app.app_context():
            usuario = (
                get_db()
                .execute(
                    "SELECT termos_aceitos_em FROM usuarios WHERE username='nova_pessoa'"
                )
                .fetchone()
            )
            self.assertIsNotNone(usuario["termos_aceitos_em"])

    def test_usuario_pode_atualizar_dados_pessoais(self):
        self.autenticar_sessao(self.comprador_id)
        resposta = self.client.post(
            "/minha-conta",
            data={
                "csrf_token": "token-teste",
                "acao": "perfil",
                "nome": "Comprador Atualizado",
                "whatsapp": "27999999995",
            },
        )
        self.assertEqual(resposta.status_code, 200)
        with app.app_context():
            usuario = (
                get_db()
                .execute(
                    "SELECT nome, whatsapp FROM usuarios WHERE id=?",
                    (self.comprador_id,),
                )
                .fetchone()
            )
            self.assertEqual(usuario["nome"], "Comprador Atualizado")
            self.assertEqual(usuario["whatsapp"], "27999999995")

    def test_usuario_pode_desativar_conta_sem_pedido_aberto(self):
        self.autenticar_sessao(self.comprador_id)
        resposta = self.client.post(
            "/minha-conta/desativar",
            data={"csrf_token": "token-teste", "senha": "senha-segura"},
        )
        self.assertEqual(resposta.status_code, 302)
        with app.app_context():
            ativo = (
                get_db()
                .execute("SELECT ativo FROM usuarios WHERE id=?", (self.comprador_id,))
                .fetchone()[0]
            )
            self.assertEqual(ativo, 0)

    def test_admin_nao_pode_desativar_a_propria_conta(self):
        self.autenticar_sessao(self.admin_id, admin=True)
        resposta = self.client.post(
            f"/admin/usuario/{self.admin_id}/toggle",
            data={"csrf_token": "token-teste"},
        )
        self.assertEqual(resposta.status_code, 302)
        with app.app_context():
            ativo = (
                get_db()
                .execute("SELECT ativo FROM usuarios WHERE id=?", (self.admin_id,))
                .fetchone()[0]
            )
            self.assertEqual(ativo, 1)

    def test_ajuda_e_recuperacao_de_acesso_estao_disponiveis(self):
        self.assertEqual(self.client.get("/ajuda").status_code, 200)
        self.assertEqual(self.client.get("/recuperar-acesso").status_code, 200)
        with self.client.session_transaction() as sessao:
            sessao["_csrf_token"] = "token-teste"
        resposta = self.client.post(
            "/recuperar-acesso",
            data={"csrf_token": "token-teste", "username": "comprador"},
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta.headers["Location"].startswith("https://wa.me/"))

    def test_formularios_permitam_mostrar_a_senha(self):
        login = self.client.get("/login")
        cadastro = self.client.get("/cadastro")

        self.assertIn(b'data-password-toggle="login-senha"', login.data)
        self.assertIn(b'data-password-toggle="cadastro-senha"', cadastro.data)
        self.assertIn(b"password-toggle.js", login.data)
        self.assertIn(b'autocomplete="current-password"', login.data)
        self.assertIn("salvar sua senha".encode(), login.data)

    def test_admin_publica_e_arquiva_comunicado_global(self):
        self.autenticar_sessao(self.admin_id, admin=True)
        resposta = self.client.post(
            "/admin/comunicado",
            data={
                "csrf_token": "token-teste",
                "titulo": "Atualização importante",
                "mensagem": "Os anúncios foram restaurados e os dados estão protegidos.",
                "tipo": "atencao",
            },
        )
        self.assertEqual(resposta.status_code, 302)

        pagina = self.client.get("/")
        self.assertIn("Atualização importante".encode(), pagina.data)
        self.assertIn("Os anúncios foram restaurados".encode(), pagina.data)

        with app.app_context():
            comunicado = get_db().execute("SELECT * FROM comunicados").fetchone()
            self.assertEqual(comunicado["ativo"], 1)

        resposta = self.client.post(
            f"/admin/comunicado/{comunicado['id']}/toggle",
            data={"csrf_token": "token-teste"},
        )
        self.assertEqual(resposta.status_code, 302)
        pagina = self.client.get("/")
        self.assertNotIn("Atualização importante".encode(), pagina.data)

    def test_novo_comunicado_arquiva_anterior_sem_apagar_historico(self):
        self.autenticar_sessao(self.admin_id, admin=True)
        for numero in (1, 2):
            self.client.post(
                "/admin/comunicado",
                data={
                    "csrf_token": "token-teste",
                    "titulo": f"Comunicado {numero}",
                    "mensagem": f"Mensagem geral número {numero}.",
                    "tipo": "informacao",
                },
            )
        with app.app_context():
            db = get_db()
            self.assertEqual(
                db.execute("SELECT COUNT(*) FROM comunicados").fetchone()[0], 2
            )
            self.assertEqual(
                db.execute("SELECT COUNT(*) FROM comunicados WHERE ativo=1").fetchone()[
                    0
                ],
                1,
            )

    def test_anuncio_aceita_bairro_e_varias_fotos(self):
        self.autenticar_sessao(self.comprador_id)
        resposta = self.client.post(
            "/criar",
            data={
                "csrf_token": "token-teste",
                "titulo": "Mesa de madeira",
                "descricao": "Mesa conservada com quatro lugares.",
                "preco": "450,00",
                "categoria": "Móveis",
                "condicao": "Usado",
                "bairro": "Centro",
                "fotos": [
                    (io.BytesIO(b"\xff\xd8\xfffoto-1"), "mesa-1.jpg"),
                    (io.BytesIO(b"\xff\xd8\xfffoto-2"), "mesa-2.jpg"),
                ],
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(resposta.status_code, 302)
        with app.app_context():
            db = get_db()
            anuncio = db.execute(
                "SELECT id, bairro, foto FROM anuncios WHERE titulo='Mesa de madeira'"
            ).fetchone()
            total_fotos = db.execute(
                "SELECT COUNT(*) FROM anuncio_fotos WHERE anuncio_id=?",
                (anuncio["id"],),
            ).fetchone()[0]
            self.assertEqual(anuncio["bairro"], "Centro")
            self.assertIsNotNone(anuncio["foto"])
            self.assertEqual(total_fotos, 2)

        pagina = self.client.get(f"/anuncio/{anuncio['id']}")
        self.assertEqual(pagina.status_code, 200)
        self.assertIn(b"product-gallery", pagina.data)
        busca = self.client.get("/?q=Centro")
        self.assertIn("Mesa de madeira".encode(), busca.data)

    def test_contato_do_anuncio_e_registrado(self):
        self.autenticar_sessao(self.comprador_id)
        resposta = self.client.get(f"/anuncio/{self.anuncio_id}/contato")
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta.headers["Location"].startswith("https://wa.me/"))
        with app.app_context():
            total = (
                get_db()
                .execute(
                    "SELECT contatos_whatsapp FROM anuncios WHERE id=?",
                    (self.anuncio_id,),
                )
                .fetchone()[0]
            )
            self.assertEqual(total, 1)

    def criar_pedido_de_teste(self):
        self.autenticar_sessao(self.comprador_id)
        resposta = self.client.post(
            f"/comprar/{self.anuncio_id}",
            data={
                "csrf_token": "token-teste",
                "entrega": "retirada",
                "observacao": "Posso buscar no fim da tarde.",
            },
        )
        self.assertEqual(resposta.status_code, 302)
        with app.app_context():
            return (
                get_db()
                .execute(
                    "SELECT id FROM pedidos WHERE anuncio_id=? AND comprador_id=?",
                    (self.anuncio_id, self.comprador_id),
                )
                .fetchone()[0]
            )

    def test_fluxo_completo_de_pedido(self):
        pedido_id = self.criar_pedido_de_teste()
        self.autenticar_sessao(self.vendedor_id)
        self.client.post(
            f"/pedido/{pedido_id}/confirmar",
            data={"csrf_token": "token-teste"},
        )
        with app.app_context():
            db = get_db()
            self.assertEqual(
                db.execute(
                    "SELECT status FROM pedidos WHERE id=?", (pedido_id,)
                ).fetchone()[0],
                "confirmado",
            )
            self.assertEqual(
                db.execute(
                    "SELECT ativo FROM anuncios WHERE id=?", (self.anuncio_id,)
                ).fetchone()[0],
                0,
            )

        self.autenticar_sessao(self.comprador_id)
        self.client.post(
            f"/pedido/{pedido_id}/concluir",
            data={"csrf_token": "token-teste"},
        )
        with app.app_context():
            pedido = (
                get_db()
                .execute(
                    "SELECT status, comprador_confirmou_em, vendedor_confirmou_em FROM pedidos WHERE id=?",
                    (pedido_id,),
                )
                .fetchone()
            )
            self.assertEqual(pedido["status"], "confirmado")
            self.assertIsNotNone(pedido["comprador_confirmou_em"])
            self.assertIsNone(pedido["vendedor_confirmou_em"])

        self.autenticar_sessao(self.vendedor_id)
        self.client.post(
            f"/pedido/{pedido_id}/concluir",
            data={"csrf_token": "token-teste"},
        )
        with app.app_context():
            pedido = (
                get_db()
                .execute(
                    "SELECT status, comprador_confirmou_em, vendedor_confirmou_em FROM pedidos WHERE id=?",
                    (pedido_id,),
                )
                .fetchone()
            )
            self.assertEqual(pedido["status"], "concluido")
            self.assertIsNotNone(pedido["comprador_confirmou_em"])
            self.assertIsNotNone(pedido["vendedor_confirmou_em"])

    def tipos_eventos(self, pedido_id):
        with app.app_context():
            return [
                linha["tipo"]
                for linha in get_db().execute(
                    "SELECT tipo FROM pedido_eventos WHERE pedido_id=? ORDER BY id",
                    (pedido_id,),
                ).fetchall()
            ]

    def preparar_dados_painel_vendedor(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "UPDATE anuncios SET estoque=2, ativo=1, visualizacoes=7, "
                "criado_em='2026-01-01 10:00:00' WHERE id=?",
                (self.anuncio_id,),
            )
            anuncios_extras = (
                ("Produto pausado", 3, 0, 3, "2026-01-02 10:00:00"),
                ("Produto esgotado", 0, 0, 5, "2026-01-03 10:00:00"),
                ("Produto sem visualizações", 5, 1, 0, "2026-01-04 10:00:00"),
            )
            for titulo, estoque, ativo, visualizacoes, criado_em in anuncios_extras:
                db.execute(
                    "INSERT INTO anuncios "
                    "(usuario_id, titulo, descricao, preco, categoria, condicao, estoque, ativo, visualizacoes, criado_em) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (
                        self.vendedor_id,
                        titulo,
                        "Produto preparado para testar o painel.",
                        "100,00",
                        "Outros",
                        "Usado",
                        estoque,
                        ativo,
                        visualizacoes,
                        criado_em,
                    ),
                )
            pedidos = (
                ("aguardando", None, None, "2026-02-01 10:00:00", "2026-02-01 10:00:00"),
                ("confirmado", "2026-02-02 12:00:00", None, "2026-02-02 10:00:00", "2026-02-02 12:00:00"),
                ("em_analise", None, None, "2026-02-03 10:00:00", "2026-02-03 13:00:00"),
                ("concluido", "2026-02-05 10:00:00", "2026-02-05 10:00:00", "2026-02-04 10:00:00", "2026-02-05 10:00:00"),
                ("cancelado", None, None, "2026-02-06 10:00:00", "2026-02-06 11:00:00"),
            )
            for status, vendedor_em, comprador_em, criado_em, atualizado_em in pedidos:
                db.execute(
                    "INSERT INTO pedidos "
                    "(anuncio_id, comprador_id, vendedor_id, valor, status, entrega, "
                    "vendedor_confirmou_em, comprador_confirmou_em, criado_em, atualizado_em) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (
                        self.anuncio_id,
                        self.comprador_id,
                        self.vendedor_id,
                        "1.200,00",
                        status,
                        "retirada",
                        vendedor_em,
                        comprador_em,
                        criado_em,
                        atualizado_em,
                    ),
                )
            db.commit()

    def test_painel_vendedor_exibe_resumo_e_estatisticas_calculadas(self):
        self.preparar_dados_painel_vendedor()
        self.autenticar_sessao(self.vendedor_id)
        pagina = self.client.get("/painel-vendedor")

        self.assertEqual(pagina.status_code, 200)
        esperados = (
            b'data-metric="anuncios_ativos" data-value="2"',
            b'data-metric="anuncios_pausados" data-value="1"',
            b'data-metric="produtos_esgotados" data-value="1"',
            b'data-metric="estoque_baixo" data-value="1"',
            b'data-metric="pedidos_aguardando_acao" data-value="1"',
            b'data-metric="pedidos_em_analise" data-value="1"',
            b'data-metric="vendas_concluidas" data-value="1"',
            b'data-stat="pedidos" data-value="5"',
            b'data-stat="taxa_conclusao" data-value="20"',
        )
        for esperado in esperados:
            self.assertIn(esperado, pagina.data)
        self.assertIn("1 dia".encode(), pagina.data)
        self.assertIn("Membro desde".encode(), pagina.data)

    def test_painel_vendedor_separa_pedidos_e_oferece_historico(self):
        self.preparar_dados_painel_vendedor()
        self.autenticar_sessao(self.vendedor_id)
        pagina = self.client.get("/painel-vendedor")

        for grupo in ("aguardando", "comprador", "analise", "concluidos", "cancelados"):
            self.assertIn(f'data-order-group="{grupo}"'.encode(), pagina.data)
        self.assertIn("Aguardando minha confirmação".encode(), pagina.data)
        self.assertIn("Aguardando comprador".encode(), pagina.data)
        self.assertEqual(pagina.data.count("Abrir histórico completo".encode()), 5)

    def test_painel_vendedor_nao_expoe_dados_de_outro_vendedor(self):
        self.preparar_dados_painel_vendedor()
        self.autenticar_sessao(self.comprador_id)
        pagina = self.client.get("/painel-vendedor")

        self.assertEqual(pagina.status_code, 200)
        self.assertNotIn("Bicicleta aro 29".encode(), pagina.data)
        self.assertNotIn("Produto pausado".encode(), pagina.data)
        self.assertNotIn("Vendedor".encode(), pagina.data)
        self.assertIn("Nenhum anúncio neste filtro".encode(), pagina.data)

    def test_painel_vendedor_exige_login(self):
        resposta = self.client.get("/painel-vendedor")
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta.headers["Location"].endswith("/login"))
        with self.client.session_transaction() as sessao:
            sessao["_csrf_token"] = "token-teste"
        salvar = self.client.post(
            "/painel-vendedor/perfil",
            data={"csrf_token": "token-teste"},
        )
        self.assertEqual(salvar.status_code, 302)
        self.assertTrue(salvar.headers["Location"].endswith("/login"))

    def test_vendedor_pode_definir_nome_e_perfil_da_loja(self):
        self.autenticar_sessao(self.vendedor_id)
        resposta = self.client.post(
            "/painel-vendedor/perfil",
            data={
                "csrf_token": "token-teste",
                "loja_nome": "  Pedal   Colatina  ",
                "loja_descricao": "Bicicletas, peças e acessórios para a região.",
                "loja_bairro": "Centro",
                "loja_whatsapp": "(27) 99999-9991",
            },
        )

        self.assertEqual(resposta.status_code, 302)
        with app.app_context():
            perfil = get_db().execute(
                "SELECT loja_nome, loja_descricao, loja_bairro, loja_whatsapp "
                "FROM usuarios WHERE id=?", (self.vendedor_id,)
            ).fetchone()
            self.assertEqual(perfil["loja_nome"], "Pedal Colatina")
            self.assertEqual(perfil["loja_bairro"], "Centro")
            self.assertEqual(perfil["loja_whatsapp"], "27999999991")
        pagina = self.client.get("/painel-vendedor")
        self.assertIn("Pedal Colatina".encode(), pagina.data)
        self.assertIn("Responsável: Vendedor".encode(), pagina.data)
        self.assertIn("Bicicletas, peças e acessórios".encode(), pagina.data)

        self.autenticar_sessao(self.comprador_id)
        painel_outro_usuario = self.client.get("/painel-vendedor")
        self.assertNotIn("Pedal Colatina".encode(), painel_outro_usuario.data)

    def test_nome_da_loja_e_exclusivo_sem_diferenciar_maiusculas(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "UPDATE usuarios SET loja_nome='Loja Central' WHERE id=?",
                (self.comprador_id,),
            )
            db.commit()
        self.autenticar_sessao(self.vendedor_id)
        resposta = self.client.post(
            "/painel-vendedor/perfil",
            data={"csrf_token": "token-teste", "loja_nome": "loja central"},
            follow_redirects=True,
        )

        self.assertIn("Este nome de loja já está em uso".encode(), resposta.data)
        with app.app_context():
            nome = get_db().execute(
                "SELECT loja_nome FROM usuarios WHERE id=?", (self.vendedor_id,)
            ).fetchone()[0]
            self.assertIsNone(nome)

    def test_perfil_da_loja_valida_nome_descricao_e_whatsapp(self):
        self.autenticar_sessao(self.vendedor_id)
        casos = (
            {"loja_nome": "AB"},
            {"loja_nome": "Loja válida", "loja_descricao": "x" * 601},
            {"loja_nome": "Loja válida", "loja_whatsapp": "123"},
        )
        for dados in casos:
            with self.subTest(dados=list(dados)):
                dados["csrf_token"] = "token-teste"
                resposta = self.client.post("/painel-vendedor/perfil", data=dados)
                self.assertEqual(resposta.status_code, 302)
        with app.app_context():
            perfil = get_db().execute(
                "SELECT loja_nome, loja_descricao, loja_whatsapp FROM usuarios WHERE id=?",
                (self.vendedor_id,),
            ).fetchone()
            self.assertIsNone(perfil["loja_nome"])
            self.assertEqual(perfil["loja_descricao"], "")
            self.assertEqual(perfil["loja_whatsapp"], "")

    def test_descricao_da_loja_aceita_ate_600_caracteres(self):
        self.autenticar_sessao(self.vendedor_id)
        descricao = "x" * 600
        resposta = self.client.post(
            "/painel-vendedor/perfil",
            data={
                "csrf_token": "token-teste",
                "loja_nome": "Loja do Vendedor",
                "loja_descricao": descricao,
            },
        )

        self.assertEqual(resposta.status_code, 302)
        with app.app_context():
            perfil = get_db().execute(
                "SELECT loja_descricao FROM usuarios WHERE id=?",
                (self.vendedor_id,),
            ).fetchone()
            self.assertEqual(perfil["loja_descricao"], descricao)

    def test_painel_usa_nome_do_vendedor_quando_loja_nao_foi_nomeada(self):
        self.autenticar_sessao(self.vendedor_id)
        pagina = self.client.get("/painel-vendedor")

        self.assertIn("<h1>Vendedor</h1>".encode(), pagina.data)
        self.assertIn("Editar perfil da loja".encode(), pagina.data)
        self.assertNotIn("Responsável: Vendedor".encode(), pagina.data)

    def test_filtros_do_painel_vendedor(self):
        self.preparar_dados_painel_vendedor()
        self.autenticar_sessao(self.vendedor_id)
        cenarios = {
            "ativos": ("Bicicleta aro 29", "Produto sem visualizações"),
            "pausados": ("Produto pausado",),
            "esgotados": ("Produto esgotado",),
            "sem_visualizacoes": ("Produto sem visualizações",),
        }
        todos_titulos = {
            "Bicicleta aro 29",
            "Produto pausado",
            "Produto esgotado",
            "Produto sem visualizações",
        }
        for filtro, presentes in cenarios.items():
            with self.subTest(filtro=filtro):
                pagina = self.client.get(f"/painel-vendedor?filtro={filtro}")
                self.assertEqual(pagina.status_code, 200)
                html = pagina.data.decode("utf-8")
                inicio = html.index('<div class="seller-products-grid">')
                fim = html.index("</section>", inicio)
                vitrine = html[inicio:fim]
                for titulo in presentes:
                    self.assertIn(titulo, vitrine)
                for titulo in todos_titulos - set(presentes):
                    self.assertNotIn(titulo, vitrine)
        mais_vistos = self.client.get("/painel-vendedor?filtro=mais_vistos").data.decode("utf-8")
        inicio = mais_vistos.index('<div class="seller-products-grid">')
        fim = mais_vistos.index("</section>", inicio)
        vitrine_mais_vistos = mais_vistos[inicio:fim]
        self.assertLess(
            vitrine_mais_vistos.find("Bicicleta aro 29"),
            vitrine_mais_vistos.find("Produto esgotado"),
        )

    def test_painel_vendedor_e_responsivo_e_nao_usa_tabelas(self):
        self.preparar_dados_painel_vendedor()
        self.autenticar_sessao(self.vendedor_id)
        pagina = self.client.get("/painel-vendedor")

        self.assertIn(b'name="viewport"', pagina.data)
        self.assertIn(b"seller-summary-grid", pagina.data)
        self.assertIn(b"seller-order-groups", pagina.data)
        self.assertNotIn(b"<table", pagina.data)
        self.assertIn("7 visualizações".encode(), pagina.data)
        self.assertNotIn("visualizaçãoões".encode(), pagina.data)
        with open(
            os.path.join(os.path.dirname(app_module.__file__), "static", "styles.css"),
            encoding="utf-8",
        ) as estilos:
            css = estilos.read()
        self.assertIn("@media(max-width:640px)", css)
        self.assertIn(".seller-order-groups", css)
        self.assertIn("grid-auto-flow:column", css)
        self.assertIn("min-width:0;max-width:100%", css)

    def preparar_loja_publica(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "UPDATE usuarios SET loja_nome=?, loja_descricao=?, loja_bairro=?, "
                "loja_whatsapp=?, criado_em=? WHERE id=?",
                (
                    "Pedal Ágil Colatina",
                    "Bicicletas, peças e acessórios para ciclistas da região.",
                    "Centro",
                    "2788887777",
                    "2025-01-15 09:00:00",
                    self.vendedor_id,
                ),
            )
            db.execute(
                "UPDATE anuncios SET titulo='Anúncio mais antigo', estoque=3, ativo=1, "
                "criado_em='2026-01-01 10:00:00' WHERE id=?",
                (self.anuncio_id,),
            )
            db.execute(
                "INSERT INTO anuncios "
                "(usuario_id, titulo, descricao, preco, categoria, condicao, estoque, ativo, criado_em) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    self.vendedor_id,
                    "Anúncio mais recente",
                    "Produto ativo da loja.",
                    "250,00",
                    "Outros",
                    "Novo",
                    2,
                    1,
                    "2026-02-01 10:00:00",
                ),
            )
            db.execute(
                "INSERT INTO anuncios "
                "(usuario_id, titulo, descricao, preco, categoria, condicao, estoque, ativo, criado_em) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    self.vendedor_id,
                    "Anúncio privado pausado",
                    "Este anúncio não pode aparecer publicamente.",
                    "99,00",
                    "Outros",
                    "Usado",
                    1,
                    0,
                    "2026-03-01 10:00:00",
                ),
            )
            db.execute(
                "INSERT INTO pedidos "
                "(anuncio_id, comprador_id, vendedor_id, valor, status, entrega, "
                "comprador_confirmou_em, criado_em, atualizado_em) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    self.anuncio_id,
                    self.comprador_id,
                    self.vendedor_id,
                    "1.200,00",
                    "concluido",
                    "retirada",
                    "2026-01-05 12:00:00",
                    "2026-01-04 10:00:00",
                    "2026-01-05 12:00:00",
                ),
            )
            db.commit()
        return f"/loja/{self.vendedor_id}-pedal-agil-colatina"

    def test_loja_publica_exibe_perfil_e_anuncios_ativos_em_ordem(self):
        caminho = self.preparar_loja_publica()
        pagina = self.client.get(caminho)
        html = pagina.data.decode("utf-8")

        self.assertEqual(pagina.status_code, 200)
        self.assertIn("Pedal Ágil Colatina", html)
        self.assertIn("Bicicletas, peças e acessórios", html)
        self.assertIn("Centro · Colatina, ES", html)
        self.assertIn("Anúncios ativos</span><strong>2", html)
        self.assertIn("Vendas concluídas</span><strong>1", html)
        self.assertIn("Produtos vendidos</span><strong>1", html)
        self.assertLess(html.index("Anúncio mais recente"), html.index("Anúncio mais antigo"))
        self.assertNotIn("Anúncio privado pausado", html)

    def test_loja_publica_usa_slug_canonico_e_atalho_por_id(self):
        caminho = self.preparar_loja_publica()
        slug_incorreto = self.client.get(f"/loja/{self.vendedor_id}-nome-antigo")
        somente_id = self.client.get(f"/loja/{self.vendedor_id}")

        self.assertEqual(slug_incorreto.status_code, 301)
        self.assertTrue(slug_incorreto.headers["Location"].endswith(caminho))
        self.assertEqual(somente_id.status_code, 301)
        self.assertTrue(somente_id.headers["Location"].endswith(caminho))
        self.assertEqual(app_module.slug_loja("Pedal Ágil Colatina"), "pedal-agil-colatina")

    def test_loja_publica_nao_expoe_dados_privados_ou_administrativos(self):
        caminho = self.preparar_loja_publica()
        pagina = self.client.get(caminho)
        html = pagina.data.decode("utf-8")

        self.assertEqual(pagina.status_code, 200)
        self.assertNotIn("27999999991", html)
        self.assertNotIn("Último acesso", html)
        self.assertNotIn("Pedidos cancelados", html)
        self.assertNotIn("Pedidos em análise", html)
        self.assertNotIn("administrador", html.lower())
        self.assertIn("https://wa.me/552788887777", html)

    def test_loja_publica_tem_seo_url_e_compartilhamento(self):
        caminho = self.preparar_loja_publica()
        pagina = self.client.get(caminho)
        html = pagina.data.decode("utf-8")

        self.assertIn("<title>Pedal Ágil Colatina | Loja no Mercado Colatina</title>", html)
        self.assertIn('property="og:title" content="Pedal Ágil Colatina | Mercado Colatina"', html)
        self.assertIn('property="og:image"', html)
        self.assertIn("mercado-colatina-social.svg", html)
        self.assertIn(f'data-share-url="http://localhost{caminho}"', html)
        self.assertIn(f'<link rel="canonical" href="http://localhost{caminho}">', html)
        self.assertIn("store-share.js", html)

    def test_visitante_acessa_loja_antes_de_abrir_anuncio(self):
        caminho = self.preparar_loja_publica()
        pagina_inicial = self.client.get("/")
        self.assertEqual(pagina_inicial.status_code, 200)
        self.assertIn(f'href="{caminho}">Conhecer a loja</a>'.encode(), pagina_inicial.data)

    def test_loja_inexistente_ou_inativa_retorna_404(self):
        self.assertEqual(self.client.get("/loja/999999-loja-inexistente").status_code, 404)
        with app.app_context():
            db = get_db()
            db.execute("UPDATE usuarios SET ativo=0 WHERE id=?", (self.vendedor_id,))
            db.commit()
        self.assertEqual(
            self.client.get(f"/loja/{self.vendedor_id}-vendedor").status_code, 404
        )

    def test_loja_publica_e_responsiva_em_desktop_tablet_e_celular(self):
        caminho = self.preparar_loja_publica()
        pagina = self.client.get(caminho)
        self.assertIn(b'name="viewport"', pagina.data)
        self.assertIn(b"public-store-hero", pagina.data)
        self.assertIn(b"public-store-stats", pagina.data)
        with open(
            os.path.join(os.path.dirname(app_module.__file__), "static", "styles.css"),
            encoding="utf-8",
        ) as estilos:
            css = estilos.read()
        self.assertIn("@media(max-width:840px){.public-store-stats", css)
        self.assertIn("@media(max-width:640px){.public-store-hero", css)

    def test_sitemap_inclui_loja_publica_com_anuncio_ativo(self):
        caminho = self.preparar_loja_publica()
        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertIn(f"http://localhost{caminho}".encode(), sitemap.data)

    def preparar_dados_reputacao(self):
        with app.app_context():
            db = get_db()
            pedidos = (
                ("concluido", "2026-03-01 10:00:00", "2026-03-02 10:00:00", "2026-03-01 22:00:00"),
                ("concluido", "2026-03-03 10:00:00", "2026-03-05 10:00:00", "2026-03-04 10:00:00"),
                ("cancelado", "2026-03-06 10:00:00", "2026-03-06 12:00:00", None),
                ("em_analise", "2026-03-07 10:00:00", "2026-03-07 13:00:00", None),
            )
            for status, criado_em, atualizado_em, comprador_em in pedidos:
                db.execute(
                    "INSERT INTO pedidos "
                    "(anuncio_id, comprador_id, vendedor_id, valor, status, entrega, "
                    "comprador_confirmou_em, criado_em, atualizado_em) "
                    "VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        self.anuncio_id,
                        self.comprador_id,
                        self.vendedor_id,
                        "1.200,00",
                        status,
                        "retirada",
                        comprador_em,
                        criado_em,
                        atualizado_em,
                    ),
                )
            db.execute(
                "UPDATE usuarios SET criado_em='2025-01-15 09:00:00', "
                "ultimo_acesso_em='2026-03-10 14:30:00' WHERE id IN (?,?)",
                (self.vendedor_id, self.comprador_id),
            )
            db.commit()

    def test_reputacao_calcula_vendedor_com_taxa_e_tempo_medio(self):
        self.preparar_dados_reputacao()
        with app.app_context():
            db = get_db()
            usuario = db.execute(
                "SELECT * FROM usuarios WHERE id=?", (self.vendedor_id,)
            ).fetchone()
            reputacao = app_module.calcular_reputacao_usuario(db, usuario)["vendedor"]

        self.assertEqual(reputacao["vendas_concluidas"], 2)
        self.assertEqual(reputacao["pedidos_concluidos"], 2)
        self.assertEqual(reputacao["pedidos_cancelados"], 1)
        self.assertEqual(reputacao["pedidos_em_analise"], 1)
        self.assertEqual(reputacao["taxa_conclusao"], 67)
        self.assertEqual(reputacao["tempo_medio_conclusao"], "1 dia")

    def test_reputacao_calcula_comprador_e_tempo_de_recebimento(self):
        self.preparar_dados_reputacao()
        with app.app_context():
            db = get_db()
            usuario = db.execute(
                "SELECT * FROM usuarios WHERE id=?", (self.comprador_id,)
            ).fetchone()
            reputacao = app_module.calcular_reputacao_usuario(db, usuario)["comprador"]

        self.assertEqual(reputacao["compras_concluidas"], 2)
        self.assertEqual(reputacao["compras_canceladas"], 1)
        self.assertEqual(reputacao["pedidos_em_analise"], 1)
        self.assertEqual(reputacao["taxa_conclusao"], 67)
        self.assertEqual(reputacao["tempo_medio_recebimento"], "18h 0min")

    def test_usuario_visualiza_apenas_a_propria_reputacao_completa(self):
        self.preparar_dados_reputacao()
        self.autenticar_sessao(self.vendedor_id)
        pagina = self.client.get("/minha-conta")

        self.assertEqual(pagina.status_code, 200)
        self.assertIn("Minha reputação".encode(), pagina.data)
        self.assertIn("Vendas concluídas".encode(), pagina.data)
        self.assertIn(b">2</dd>", pagina.data)
        self.assertNotIn(b"@comprador", pagina.data)
        bloqueado = self.client.get(f"/admin/reputacao/{self.comprador_id}")
        self.assertEqual(bloqueado.status_code, 302)
        self.assertTrue(bloqueado.headers["Location"].endswith("/"))

    def test_admin_visualiza_reputacao_completa_de_qualquer_usuario(self):
        self.preparar_dados_reputacao()
        self.autenticar_sessao(self.admin_id, admin=True)
        pagina = self.client.get(f"/admin/reputacao/{self.comprador_id}")

        self.assertEqual(pagina.status_code, 200)
        self.assertIn(b"@comprador", pagina.data)
        self.assertIn("Compras concluídas".encode(), pagina.data)
        self.assertIn("Último acesso".encode(), pagina.data)

    def test_reputacao_publica_expoe_somente_indicadores_permitidos(self):
        self.preparar_dados_reputacao()
        pagina = self.client.get(f"/anuncio/{self.anuncio_id}")
        html = pagina.data.decode("utf-8")
        inicio = html.index('<div class="public-reputation"')
        fim = html.index("</dl>", inicio)
        reputacao_publica = html[inicio:fim]

        self.assertIn("Membro desde", reputacao_publica)
        self.assertIn("Vendas concluídas", reputacao_publica)
        self.assertIn("Taxa de conclusão", reputacao_publica)
        for privado in ("Último acesso", "Pedidos cancelados", "Pedidos em análise", "Tempo médio"):
            self.assertNotIn(privado, reputacao_publica)

    def test_usuario_nao_pode_editar_indicadores_de_reputacao(self):
        self.autenticar_sessao(self.vendedor_id)
        self.client.post(
            "/minha-conta",
            data={
                "csrf_token": "token-teste",
                "acao": "perfil",
                "nome": "Vendedor Atualizado",
                "whatsapp": "27999999991",
                "loja_verificada": "1",
                "vendas_concluidas": "999",
            },
        )
        with app.app_context():
            verificada = get_db().execute(
                "SELECT loja_verificada FROM usuarios WHERE id=?", (self.vendedor_id,)
            ).fetchone()[0]
            pedidos = get_db().execute(
                "SELECT COUNT(*) FROM pedidos WHERE vendedor_id=?", (self.vendedor_id,)
            ).fetchone()[0]
        self.assertEqual(verificada, 0)
        self.assertEqual(pedidos, 0)

    def test_login_bem_sucedido_registra_ultimo_acesso(self):
        with self.client.session_transaction() as sessao:
            sessao["_csrf_token"] = "token-teste"
        falha = self.client.post(
            "/login",
            data={
                "csrf_token": "token-teste",
                "username": "vendedor",
                "senha": "incorreta",
            },
        )
        self.assertEqual(falha.status_code, 200)
        with app.app_context():
            antes = get_db().execute(
                "SELECT ultimo_acesso_em FROM usuarios WHERE id=?", (self.vendedor_id,)
            ).fetchone()[0]
        self.assertIsNone(antes)

        sucesso = self.client.post(
            "/login",
            data={
                "csrf_token": "token-teste",
                "username": "vendedor",
                "senha": "senha-segura",
            },
        )
        self.assertEqual(sucesso.status_code, 302)
        with app.app_context():
            depois = get_db().execute(
                "SELECT ultimo_acesso_em FROM usuarios WHERE id=?", (self.vendedor_id,)
            ).fetchone()[0]
        self.assertIsNotNone(depois)

    def test_criacao_do_pedido_gera_evento_inicial(self):
        pedido_id = self.criar_pedido_de_teste()
        with app.app_context():
            evento = get_db().execute(
                "SELECT * FROM pedido_eventos WHERE pedido_id=? AND tipo='PEDIDO_CRIADO'",
                (pedido_id,),
            ).fetchone()
            self.assertIsNotNone(evento)
            self.assertEqual(evento["usuario_id"], self.comprador_id)
            self.assertEqual(evento["papel_usuario"], "comprador")
            self.assertEqual(evento["estado_posterior"], "aguardando")

    def test_confirmacao_registra_vendedor_e_reserva_de_estoque(self):
        pedido_id = self.criar_pedido_de_teste()
        self.autenticar_sessao(self.vendedor_id)
        self.client.post(
            f"/pedido/{pedido_id}/confirmar", data={"csrf_token": "token-teste"}
        )
        tipos = self.tipos_eventos(pedido_id)
        self.assertIn("VENDEDOR_CONFIRMOU", tipos)
        self.assertIn("ESTOQUE_RESERVADO", tipos)
        with app.app_context():
            evento_sistema = get_db().execute(
                "SELECT papel_usuario FROM pedido_eventos "
                "WHERE pedido_id=? AND tipo='ESTOQUE_RESERVADO'", (pedido_id,)
            ).fetchone()
            self.assertEqual(evento_sistema["papel_usuario"], "sistema")

    def test_dupla_confirmacao_registra_eventos_e_conclusao(self):
        pedido_id = self.criar_pedido_de_teste()
        self.autenticar_sessao(self.vendedor_id)
        self.client.post(
            f"/pedido/{pedido_id}/confirmar", data={"csrf_token": "token-teste"}
        )
        self.client.post(
            f"/pedido/{pedido_id}/concluir", data={"csrf_token": "token-teste"}
        )
        self.autenticar_sessao(self.comprador_id)
        self.client.post(
            f"/pedido/{pedido_id}/concluir", data={"csrf_token": "token-teste"}
        )
        tipos = self.tipos_eventos(pedido_id)
        self.assertIn("VENDA_MARCADA_COMO_REALIZADA", tipos)
        self.assertIn("COMPRADOR_CONFIRMOU_RECEBIMENTO", tipos)
        self.assertIn("PEDIDO_CONCLUIDO", tipos)
        with app.app_context():
            conclusao = get_db().execute(
                "SELECT papel_usuario FROM pedido_eventos "
                "WHERE pedido_id=? AND tipo='PEDIDO_CONCLUIDO'", (pedido_id,)
            ).fetchone()
            self.assertEqual(conclusao["papel_usuario"], "sistema")

    def test_vendedor_sozinho_nao_conclui_pedido(self):
        pedido_id = self.criar_pedido_de_teste()
        self.autenticar_sessao(self.vendedor_id)
        self.client.post(
            f"/pedido/{pedido_id}/confirmar",
            data={"csrf_token": "token-teste"},
        )
        self.client.post(
            f"/pedido/{pedido_id}/concluir",
            data={"csrf_token": "token-teste"},
        )
        with app.app_context():
            pedido = get_db().execute(
                "SELECT status, vendedor_confirmou_em, comprador_confirmou_em FROM pedidos WHERE id=?",
                (pedido_id,),
            ).fetchone()
            self.assertEqual(pedido["status"], "confirmado")
            self.assertIsNotNone(pedido["vendedor_confirmou_em"])
            self.assertIsNone(pedido["comprador_confirmou_em"])

    def test_confirmar_pedido_reserva_uma_unidade_do_estoque(self):
        with app.app_context():
            db = get_db()
            db.execute("UPDATE anuncios SET estoque=2 WHERE id=?", (self.anuncio_id,))
            db.commit()

        pedido_id = self.criar_pedido_de_teste()
        self.autenticar_sessao(self.vendedor_id)
        self.client.post(
            f"/pedido/{pedido_id}/confirmar",
            data={"csrf_token": "token-teste"},
        )

        with app.app_context():
            anuncio = get_db().execute(
                "SELECT estoque, ativo FROM anuncios WHERE id=?", (self.anuncio_id,)
            ).fetchone()
            self.assertEqual(anuncio["estoque"], 1)
            self.assertEqual(anuncio["ativo"], 1)

    def test_cancelar_pedido_reservado_devolve_estoque(self):
        pedido_id = self.criar_pedido_de_teste()
        self.autenticar_sessao(self.vendedor_id)
        self.client.post(
            f"/pedido/{pedido_id}/confirmar",
            data={"csrf_token": "token-teste"},
        )

        self.autenticar_sessao(self.comprador_id)
        self.client.post(
            f"/pedido/{pedido_id}/cancelar",
            data={"csrf_token": "token-teste"},
        )

        with app.app_context():
            anuncio = get_db().execute(
                "SELECT estoque, ativo FROM anuncios WHERE id=?", (self.anuncio_id,)
            ).fetchone()
            self.assertEqual(anuncio["estoque"], 1)
            self.assertEqual(anuncio["ativo"], 1)
        tipos = self.tipos_eventos(pedido_id)
        self.assertIn("PEDIDO_CANCELADO", tipos)
        self.assertIn("ESTOQUE_DEVOLVIDO", tipos)

    def test_usuario_pode_enviar_pedido_confirmado_para_analise(self):
        pedido_id = self.criar_pedido_de_teste()
        self.autenticar_sessao(self.vendedor_id)
        self.client.post(
            f"/pedido/{pedido_id}/confirmar",
            data={"csrf_token": "token-teste"},
        )
        self.autenticar_sessao(self.comprador_id)
        self.client.post(
            f"/pedido/{pedido_id}/problema",
            data={
                "csrf_token": "token-teste",
                "motivo": "PRODUTO_NAO_ENTREGUE",
                "descricao": "A entrega combinada não aconteceu.",
            },
        )
        with app.app_context():
            db = get_db()
            pedido = db.execute(
                "SELECT status, problema_motivo, problema_descricao, problema_relator_id "
                "FROM pedidos WHERE id=?", (pedido_id,)
            ).fetchone()
            self.assertEqual(pedido["status"], "em_analise")
            self.assertEqual(pedido["problema_motivo"], "PRODUTO_NAO_ENTREGUE")
            self.assertEqual(pedido["problema_relator_id"], self.comprador_id)
            self.assertIn("entrega", pedido["problema_descricao"])
        tipos = self.tipos_eventos(pedido_id)
        self.assertIn("PROBLEMA_RELATADO", tipos)
        self.assertIn("PEDIDO_EM_ANALISE", tipos)
        self.autenticar_sessao(self.comprador_id)
        historico = self.client.get(f"/pedido/{pedido_id}/historico")
        self.assertIn("Produto não entregue".encode(), historico.data)
        self.assertNotIn("A entrega combinada não aconteceu.".encode(), historico.data)
        self.autenticar_sessao(self.admin_id, admin=True)
        painel = self.client.get("/admin")
        self.assertIn("A entrega combinada não aconteceu.".encode(), painel.data)

    def test_relatar_problema_exige_motivo_e_outro_exige_descricao(self):
        pedido_id = self.criar_pedido_de_teste()
        self.autenticar_sessao(self.vendedor_id)
        self.client.post(
            f"/pedido/{pedido_id}/confirmar", data={"csrf_token": "token-teste"}
        )
        self.autenticar_sessao(self.comprador_id)
        sem_motivo = self.client.post(
            f"/pedido/{pedido_id}/problema", data={"csrf_token": "token-teste"}
        )
        outro_sem_descricao = self.client.post(
            f"/pedido/{pedido_id}/problema",
            data={"csrf_token": "token-teste", "motivo": "OUTRO"},
        )
        self.assertEqual(sem_motivo.status_code, 302)
        self.assertEqual(outro_sem_descricao.status_code, 302)
        with app.app_context():
            pedido = get_db().execute(
                "SELECT status, problema_motivo FROM pedidos WHERE id=?", (pedido_id,)
            ).fetchone()
            self.assertEqual(pedido["status"], "confirmado")
            self.assertIsNone(pedido["problema_motivo"])
        self.assertNotIn("PROBLEMA_RELATADO", self.tipos_eventos(pedido_id))

    def test_relatar_problema_nao_altera_estoque(self):
        pedido_id = self.criar_pedido_de_teste()
        self.autenticar_sessao(self.vendedor_id)
        self.client.post(
            f"/pedido/{pedido_id}/confirmar", data={"csrf_token": "token-teste"}
        )
        with app.app_context():
            estoque_antes = get_db().execute(
                "SELECT estoque FROM anuncios WHERE id=?", (self.anuncio_id,)
            ).fetchone()[0]
        self.autenticar_sessao(self.comprador_id)
        self.client.post(
            f"/pedido/{pedido_id}/problema",
            data={"csrf_token": "token-teste", "motivo": "VENDEDOR_NAO_RESPONDE"},
        )
        with app.app_context():
            estoque_depois = get_db().execute(
                "SELECT estoque FROM anuncios WHERE id=?", (self.anuncio_id,)
            ).fetchone()[0]
            self.assertEqual(estoque_depois, estoque_antes)

    def test_historico_respeita_permissoes_de_comprador_vendedor_e_admin(self):
        pedido_id = self.criar_pedido_de_teste()
        self.autenticar_sessao(self.comprador_id)
        self.assertEqual(
            self.client.get(f"/pedido/{pedido_id}/historico").status_code, 200
        )
        self.autenticar_sessao(self.vendedor_id)
        self.assertEqual(
            self.client.get(f"/pedido/{pedido_id}/historico").status_code, 200
        )
        self.autenticar_sessao(self.admin_id, admin=True)
        self.assertEqual(
            self.client.get(f"/pedido/{pedido_id}/historico").status_code, 200
        )
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO usuarios (nome, username, senha, whatsapp) VALUES (?,?,?,?)",
                ("Pessoa alheia", "alheio", generate_password_hash("senha-segura"), "27999999994"),
            )
            alheio_id = db.execute(
                "SELECT id FROM usuarios WHERE username='alheio'"
            ).fetchone()[0]
            db.commit()
        self.autenticar_sessao(alheio_id)
        self.assertEqual(
            self.client.get(f"/pedido/{pedido_id}/historico").status_code, 403
        )

    def test_eventos_nao_sao_duplicados_por_cliques_repetidos(self):
        pedido_id = self.criar_pedido_de_teste()
        self.autenticar_sessao(self.vendedor_id)
        for _ in range(2):
            self.client.post(
                f"/pedido/{pedido_id}/confirmar", data={"csrf_token": "token-teste"}
            )
        self.client.post(
            f"/pedido/{pedido_id}/concluir", data={"csrf_token": "token-teste"}
        )
        self.client.post(
            f"/pedido/{pedido_id}/concluir", data={"csrf_token": "token-teste"}
        )
        with app.app_context():
            db = get_db()
            for tipo in ("VENDEDOR_CONFIRMOU", "ESTOQUE_RESERVADO", "VENDA_MARCADA_COMO_REALIZADA"):
                total = db.execute(
                    "SELECT COUNT(*) FROM pedido_eventos WHERE pedido_id=? AND tipo=?",
                    (pedido_id, tipo),
                ).fetchone()[0]
                self.assertEqual(total, 1)
            estoque = db.execute(
                "SELECT estoque FROM anuncios WHERE id=?", (self.anuncio_id,)
            ).fetchone()[0]
            self.assertEqual(estoque, 0)

    def test_pedido_legado_recebe_marco_inicial_e_continua_funcionando(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO pedidos (anuncio_id, comprador_id, vendedor_id, valor, status) "
                "VALUES (?,?,?,?,?)",
                (self.anuncio_id, self.comprador_id, self.vendedor_id, "1.200,00", "aguardando"),
            )
            pedido_id = db.execute("SELECT MAX(id) FROM pedidos").fetchone()[0]
            db.commit()
        init_db()
        self.assertEqual(self.tipos_eventos(pedido_id), ["PEDIDO_CRIADO"])
        with app.app_context():
            evento = get_db().execute(
                "SELECT usuario_id, papel_usuario, dados_adicionais FROM pedido_eventos "
                "WHERE pedido_id=?", (pedido_id,)
            ).fetchone()
            self.assertIsNone(evento["usuario_id"])
            self.assertEqual(evento["papel_usuario"], "sistema")
            self.assertIn('"legado":true', evento["dados_adicionais"])
        self.autenticar_sessao(self.vendedor_id)
        self.client.post(
            f"/pedido/{pedido_id}/confirmar", data={"csrf_token": "token-teste"}
        )
        with app.app_context():
            status = get_db().execute(
                "SELECT status FROM pedidos WHERE id=?", (pedido_id,)
            ).fetchone()[0]
            self.assertEqual(status, "confirmado")

    def test_novo_pedido_dispara_email_administrativo_e_registra_envio(self):
        with patch.object(
            app_module, "enviar_alerta_novo_pedido", return_value="enviado"
        ) as enviar:
            pedido_id = self.criar_pedido_de_teste()

        enviar.assert_called_once()
        with app.app_context():
            pedido = get_db().execute(
                "SELECT admin_email_status, admin_email_enviado_em FROM pedidos WHERE id=?",
                (pedido_id,),
            ).fetchone()
            self.assertEqual(pedido["admin_email_status"], "enviado")
            self.assertIsNotNone(pedido["admin_email_enviado_em"])

    def test_admin_recebe_alerta_grande_para_pedido_pendente(self):
        pedido_id = self.criar_pedido_de_teste()
        self.autenticar_sessao(self.admin_id, admin=True)
        painel = self.client.get("/admin")

        self.assertEqual(painel.status_code, 200)
        self.assertIn(b"admin-sales-alert", painel.data)
        self.assertIn(f"Pedido #{pedido_id}".encode(), painel.data)
        self.assertIn(b"Reenviar e-mail", painel.data)
        self.assertIn(b"Central de pedidos", painel.data)

    def test_admin_pode_enviar_email_de_teste(self):
        self.autenticar_sessao(self.admin_id, admin=True)
        with patch.object(
            app_module, "enviar_teste_admin", return_value="enviado"
        ) as enviar:
            resposta = self.client.post(
                "/admin/email/teste",
                data={"csrf_token": "token-teste"},
            )

        self.assertEqual(resposta.status_code, 302)
        enviar.assert_called_once()

    def test_admin_pode_reenviar_alerta_de_pedido(self):
        with patch.object(app_module, "enviar_alerta_novo_pedido", return_value="falhou"):
            pedido_id = self.criar_pedido_de_teste()

        self.autenticar_sessao(self.admin_id, admin=True)
        with patch.object(
            app_module, "enviar_alerta_novo_pedido", return_value="enviado"
        ) as enviar:
            resposta = self.client.post(
                f"/admin/pedido/{pedido_id}/reenviar-email",
                data={"csrf_token": "token-teste"},
            )

        self.assertEqual(resposta.status_code, 302)
        enviar.assert_called_once()
        with app.app_context():
            pedido = get_db().execute(
                "SELECT admin_email_status, admin_email_enviado_em FROM pedidos WHERE id=?",
                (pedido_id,),
            ).fetchone()
            self.assertEqual(pedido["admin_email_status"], "enviado")
            self.assertIsNotNone(pedido["admin_email_enviado_em"])

    def test_admin_exibe_texto_do_email_com_acentuacao_correta(self):
        self.autenticar_sessao(self.admin_id, admin=True)
        with patch.dict(
            os.environ, {"ADMIN_NOTIFICATION_EMAIL": "pelers@gmail.com"}
        ):
            painel = self.client.get("/admin")

        self.assertIn(
            "Nenhum pedido aguardando atenção neste momento.".encode(), painel.data
        )
        self.assertIn("o serviço remetente ainda precisa ser ativado.".encode(), painel.data)
        self.assertIn(b"admin-email-warning", painel.data)
        self.assertIn("ATENÇÃO".encode(), painel.data)
        self.assertNotIn("atenÃ§Ã£o".encode(), painel.data)

    def test_cancelamento_nao_reativa_anuncio_retirado_pela_moderacao(self):
        pedido_id = self.criar_pedido_de_teste()
        self.autenticar_sessao(self.vendedor_id)
        self.client.post(
            f"/pedido/{pedido_id}/confirmar",
            data={"csrf_token": "token-teste"},
        )
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO denuncias (anuncio_id, denunciante_id, motivo, status) VALUES (?,?,?,'resolvida')",
                (self.anuncio_id, self.comprador_id, "enganoso"),
            )
            db.commit()

        self.autenticar_sessao(self.comprador_id)
        self.client.post(
            f"/pedido/{pedido_id}/cancelar",
            data={"csrf_token": "token-teste"},
        )
        with app.app_context():
            db = get_db()
            ativo = db.execute(
                "SELECT ativo FROM anuncios WHERE id=?", (self.anuncio_id,)
            ).fetchone()[0]
            self.assertEqual(ativo, 0)

    def test_login_bloqueia_tentativas_repetidas_sem_expor_ip(self):
        with self.client.session_transaction() as sessao:
            sessao["_csrf_token"] = "token-teste"
        for _ in range(5):
            resposta = self.client.post(
                "/login",
                data={
                    "csrf_token": "token-teste",
                    "username": "comprador",
                    "senha": "senha-incorreta",
                },
            )
            self.assertEqual(resposta.status_code, 200)
        bloqueada = self.client.post(
            "/login",
            data={
                "csrf_token": "token-teste",
                "username": "comprador",
                "senha": "senha-segura",
            },
        )
        self.assertEqual(bloqueada.status_code, 429)
        with app.app_context():
            registro = (
                get_db()
                .execute("SELECT chave, bloqueado_ate FROM tentativas_login")
                .fetchone()
            )
            self.assertEqual(len(registro["chave"]), 64)
            self.assertGreater(int(registro["bloqueado_ate"]), 0)

    def test_neo_cria_rascunho_sem_publicar_automaticamente(self):
        self.autenticar_sessao(self.comprador_id)
        rascunho = {
            "titulo": "Bicicleta aro 29 usada",
            "descricao": "Bicicleta usada e conservada. Confirme marca e acessórios antes de publicar.",
            "categoria": "Outros",
            "condicao": "Usado",
            "requer_revisao": False,
            "alerta": "",
        }
        with (
            patch("app.neo_configurado", return_value=True),
            patch("app.gerar_rascunho", return_value=rascunho),
        ):
            resposta = self.client.post(
                "/neo/anuncio",
                data={
                    "csrf_token": "token-teste",
                    "relato": "Tenho uma bicicleta aro 29 usada e conservada.",
                },
            )
        self.assertEqual(resposta.status_code, 302)
        pagina = self.client.get("/criar")
        self.assertIn("Bicicleta aro 29 usada".encode(), pagina.data)
        with app.app_context():
            total = (
                get_db()
                .execute(
                    "SELECT COUNT(*) FROM anuncios WHERE titulo='Bicicleta aro 29 usada'"
                )
                .fetchone()[0]
            )
            self.assertEqual(total, 0)

    def test_todas_as_paginas_principais_renderizam(self):
        publicas = (
            "/",
            "/login",
            "/cadastro",
            "/recuperar-acesso",
            "/ajuda",
            "/seguranca",
            "/privacidade",
            "/termos",
            "/robots.txt",
            "/sitemap.xml",
            "/health",
        )
        for caminho in publicas:
            with self.subTest(caminho=caminho):
                self.assertEqual(self.client.get(caminho).status_code, 200)

        self.autenticar_sessao(self.comprador_id)
        autenticadas = (
            "/",
            "/minha-conta",
            "/criar",
            "/meus-anuncios",
            "/painel-vendedor",
            "/pedidos",
            "/assinar",
            f"/anuncio/{self.anuncio_id}",
            f"/comprar/{self.anuncio_id}",
        )
        for caminho in autenticadas:
            with self.subTest(caminho=caminho):
                self.assertEqual(self.client.get(caminho).status_code, 200)

        self.autenticar_sessao(self.admin_id, admin=True)
        self.assertEqual(self.client.get("/admin").status_code, 200)

    def test_home_destaca_promocoes_do_mercado_livre_com_aviso_de_afiliado(self):
        pagina = self.client.get("/")

        self.assertEqual(pagina.status_code, 200)
        self.assertIn(
            "Agora em Colatina e na Região Noroeste do Espírito Santo!".encode(),
            pagina.data,
        )
        self.assertIn("OFERTAS NO MERCADO LIVRE".encode(), pagina.data)
        self.assertIn(
            "Promoções incríveis selecionadas pelo Mercado Colatina".encode(),
            pagina.data,
        )
        self.assertNotIn("Paulo Eler".encode(), pagina.data)
        self.assertIn("VER PROMOÇÕES NO MERCADO LIVRE".encode(), pagina.data)
        self.assertIn("Você será direcionado para o Mercado Livre".encode(), pagina.data)
        self.assertIn(b'rel="sponsored nofollow"', pagina.data)

    def test_formulario_sem_csrf_nao_altera_dados(self):
        self.autenticar_sessao(self.comprador_id)
        resposta = self.client.post(
            f"/anuncio/{self.anuncio_id}/denunciar",
            data={"motivo": "enganoso"},
        )
        self.assertEqual(resposta.status_code, 302)
        with app.app_context():
            total = get_db().execute("SELECT COUNT(*) FROM denuncias").fetchone()[0]
            self.assertEqual(total, 0)

    def test_producao_recusa_configuracao_incompleta(self):
        with (
            patch.object(app_module, "FLASK_ENV", "production"),
            patch.dict(os.environ, {}, clear=True),
        ):
            with self.assertRaises(RuntimeError):
                app_module.validar_configuracao_producao()


if __name__ == "__main__":
    unittest.main()
