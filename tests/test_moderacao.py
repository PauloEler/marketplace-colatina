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
from database import USE_PG, get_db  # noqa: E402


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
            data={"csrf_token": "token-teste"},
        )
        with app.app_context():
            status = get_db().execute(
                "SELECT status FROM pedidos WHERE id=?", (pedido_id,)
            ).fetchone()[0]
            self.assertEqual(status, "em_analise")

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
        self.assertIn("OFERTAS NO MERCADO LIVRE".encode(), pagina.data)
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
