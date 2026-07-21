import io
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from werkzeug.security import generate_password_hash


TEST_DIR = tempfile.mkdtemp(prefix="mercado-colatina-tests-")
os.environ.pop("DATABASE_URL", None)
os.environ.pop("RESTORED_DATABASE_URL", None)
os.environ["DATABASE_PATH"] = os.path.join(TEST_DIR, "test.db")
os.environ["FLASK_ENV"] = "testing"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ.pop("STORE_MANAGER_ASSIGNMENTS", None)
os.environ.pop("HOME_CIDADE_VIVA_ENABLED", None)
os.environ.pop("HOME_CIDADE_VIVA_PRODUCT_LIMIT", None)
for indice_oferta in range(1, 7):
    os.environ.pop(f"OFERTA_PARCEIRO_{indice_oferta:02d}_URL", None)

import app as app_module  # noqa: E402
from app import app  # noqa: E402
from database import (  # noqa: E402
    USE_PG,
    _backfill_fundadores,
    _seed_loja_administradores,
    get_db,
    init_db,
)
from partner_offers import (  # noqa: E402
    PARTNER_OFFERS_CONFIG,
    build_partner_offers,
)
from community_intelligence import (  # noqa: E402
    INTELLIGENCE_SCHEMA_VERSION,
    construir_dataset_inteligencia,
    construir_inteligencia_comunidade,
)
from traction_metrics import (  # noqa: E402
    build_traction_dashboard,
    classify_access_source,
    record_access_source,
    record_user_activity,
    render_weekly_report,
)
from operation_100 import build_operation_100_dashboard  # noqa: E402
from commercial_growth import (  # noqa: E402
    build_commercial_dashboard,
    create_ambassador,
    create_company,
    create_weekly_mission,
    render_commercial_weekly_report,
    update_company_checklist,
)


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
                "growth_weekly_missions",
                "growth_ambassadors",
                "growth_commercial_companies",
                "traction_user_activity_daily",
                "traction_access_source_daily",
                "pedidos_servico",
                "sugestoes_comunidade",
                "notifications",
                "afiliado_eventos",
                "loja_administradores",
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

    def vincular_loja_ao_gestor(self, gestor_id, loja_id):
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO loja_administradores (administrador_id, loja_id) VALUES (?,?)",
                (gestor_id, loja_id),
            )
            db.commit()

    def test_gestor_escolhe_entre_duas_lojas_sem_misturar_anuncios(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "UPDATE usuarios SET loja_nome='Topa Tudo Colatinense' WHERE id=?",
                (self.vendedor_id,),
            )
            db.execute(
                "UPDATE usuarios SET loja_nome='Loja Oficial do Mercado Colatina' WHERE id=?",
                (self.admin_id,),
            )
            db.execute(
                "INSERT INTO anuncios (usuario_id, titulo, descricao, preco, categoria, condicao) "
                "VALUES (?,?,?,?,?,?)",
                (
                    self.admin_id,
                    "Produto da loja oficial",
                    "Anuncio separado da loja oficial",
                    "99,00",
                    "Outros",
                    "Novo",
                ),
            )
            db.commit()
        self.vincular_loja_ao_gestor(self.vendedor_id, self.admin_id)
        self.autenticar_sessao(self.vendedor_id)

        pagina = self.client.get("/minhas-lojas")
        self.assertEqual(pagina.status_code, 200)
        self.assertIn("Topa Tudo Colatinense", pagina.get_data(as_text=True))
        self.assertIn("Loja Oficial do Mercado Colatina", pagina.get_data(as_text=True))

        resposta = self.client.post(
            f"/minhas-lojas/{self.admin_id}/selecionar",
            data={"csrf_token": "token-teste"},
        )
        self.assertEqual(resposta.status_code, 302)
        with self.client.session_transaction() as sessao:
            self.assertEqual(sessao["loja_ativa_id"], self.admin_id)

        anuncios = self.client.get("/meus-anuncios").get_data(as_text=True)
        self.assertIn("Produto da loja oficial", anuncios)
        self.assertNotIn("Bicicleta aro 29", anuncios)

    def test_vendedor_pode_excluir_produto_sem_apagar_historico(self):
        self.autenticar_sessao(self.vendedor_id)

        pagina = self.client.get("/meus-anuncios")
        html = pagina.get_data(as_text=True)
        self.assertIn(f'action="/deletar/{self.anuncio_id}"', html)
        self.assertIn(">Excluir</button>", html)

        resposta = self.client.post(
            f"/deletar/{self.anuncio_id}",
            data={"csrf_token": "token-teste"},
            follow_redirects=True,
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertNotIn("Bicicleta aro 29", resposta.get_data(as_text=True))

        with app.app_context():
            anuncio = (
                get_db()
                .execute(
                    "SELECT ativo, excluido_em FROM anuncios WHERE id=?",
                    (self.anuncio_id,),
                )
                .fetchone()
            )
            self.assertEqual(anuncio["ativo"], 0)
            self.assertIsNotNone(anuncio["excluido_em"])

    def test_usuario_nao_pode_selecionar_loja_sem_vinculo(self):
        self.autenticar_sessao(self.comprador_id)
        resposta = self.client.post(
            f"/minhas-lojas/{self.admin_id}/selecionar",
            data={"csrf_token": "token-teste"},
        )
        self.assertEqual(resposta.status_code, 403)

    def test_login_com_duas_lojas_abre_seletor(self):
        self.vincular_loja_ao_gestor(self.vendedor_id, self.admin_id)
        with self.client.session_transaction() as sessao:
            sessao["_csrf_token"] = "token-teste"
        resposta = self.client.post(
            "/login",
            data={
                "csrf_token": "token-teste",
                "username": "vendedor",
                "senha": "senha-segura",
            },
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta.headers["Location"].endswith("/minhas-lojas"))

    def test_vinculo_padrao_ativa_as_duas_contas_oficiais(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "UPDATE usuarios SET username='topatudocolatinense' WHERE id=?",
                (self.vendedor_id,),
            )
            db.execute(
                "UPDATE usuarios SET username='admin' WHERE id=?", (self.admin_id,)
            )
            _seed_loja_administradores(db)
            db.commit()
            vinculos = {
                (linha["administrador_id"], linha["loja_id"])
                for linha in db.execute(
                    "SELECT administrador_id, loja_id FROM loja_administradores"
                ).fetchall()
            }
        self.assertIn((self.vendedor_id, self.admin_id), vinculos)
        self.assertIn((self.admin_id, self.vendedor_id), vinculos)

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

    def test_cockpit_executivo_e_exclusivo_para_admin_e_preserva_painel(self):
        visitante = self.client.get("/admin?visao=cockpit")
        self.assertEqual(visitante.status_code, 302)
        self.assertEqual(visitante.headers["Location"], "/")

        self.autenticar_sessao(self.comprador_id)
        usuario = self.client.get("/admin?visao=cockpit")
        self.assertEqual(usuario.status_code, 302)
        self.assertEqual(usuario.headers["Location"], "/")

        self.autenticar_sessao(self.admin_id, admin=True)
        cockpit = self.client.get("/admin?visao=cockpit")
        painel = self.client.get("/admin")
        html_cockpit = cockpit.data.decode("utf-8")
        conteudo_cockpit = html_cockpit.split('id="cockpit-conteudo"', 1)[1]

        self.assertEqual(cockpit.status_code, 200)
        self.assertIn('<body class="mds-cockpit">', html_cockpit)
        self.assertEqual(html_cockpit.count("<h1"), 1)
        self.assertIn("Cockpit Executivo", html_cockpit)
        self.assertNotIn("<form", conteudo_cockpit)
        self.assertIn("Painel admin".encode(), painel.data)
        self.assertNotIn(b'class="cockpit-shell"', painel.data)
        self.assertNotIn("/cockpit", {regra.rule for regra in app.url_map.iter_rules()})

    def test_cockpit_exibe_saude_metricas_operacao_alertas_e_acessibilidade(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "UPDATE usuarios SET loja_nome='Loja do Vendedor' WHERE id=?",
                (self.vendedor_id,),
            )
            db.execute(
                "INSERT INTO pedidos "
                "(anuncio_id, comprador_id, vendedor_id, valor, status) "
                "VALUES (?,?,?,?,?)",
                (
                    self.anuncio_id,
                    self.comprador_id,
                    self.vendedor_id,
                    "1.200,00",
                    "em_analise",
                ),
            )
            db.execute(
                "INSERT INTO denuncias "
                "(anuncio_id, denunciante_id, motivo, detalhes, status) "
                "VALUES (?,?,?,?,?)",
                (
                    self.anuncio_id,
                    self.comprador_id,
                    "enganoso",
                    "Informação divergente.",
                    "pendente",
                ),
            )
            db.commit()

        self.autenticar_sessao(self.admin_id, admin=True)
        ambiente = {
            "RENDER": "true",
            "RENDER_GIT_COMMIT": "1234567890abcdef1234567890abcdef12345678",
            "RENDER_DEPLOY_ID": "dep-teste-006",
            "CI_STATUS": "success",
            "CI_TEST_COUNT": "86",
        }
        with patch.dict(os.environ, ambiente, clear=False):
            pagina = self.client.get("/admin?visao=cockpit")
        html = pagina.data.decode("utf-8")

        self.assertEqual(pagina.status_code, 200)
        for indicador, valor in (
            ("anuncios_ativos", 1),
            ("usuarios_cadastrados", 3),
            ("lojas_cadastradas", 1),
            ("pedidos", 1),
            ("solicitacoes_compra", 0),
        ):
            self.assertIn(f'data-metric="{indicador}" data-value="{valor}"', html)
        for texto in (
            "HTTP 200",
            "dep-teste-006",
            "1234567890ab",
            "Aprovado",
            ">86<",
            "Produção · Render",
            "Denúncias aguardando análise",
            "Pedidos em análise",
            "Bicicleta aro 29",
            "@comprador",
            "Novo anúncio",
            "Minha Loja",
            "Administração",
        ):
            self.assertIn(texto, html)
        for titulo in (
            "cockpit-health-title",
            "cockpit-market-title",
            "cockpit-operation-title",
            "cockpit-alerts-title",
            "cockpit-actions-title",
        ):
            self.assertIn(f'aria-labelledby="{titulo}"', html)

        with open(
            os.path.join(app.root_path, "static", "styles.css"), encoding="utf-8"
        ) as arquivo_css:
            css = arquivo_css.read()
        self.assertIn(".mds-cockpit", css)
        self.assertIn("@media(max-width:639px)", css)
        self.assertIn("@media(prefers-reduced-motion:reduce)", css)

    def test_dashboard_executivo_e_exclusivo_para_admin_e_preserva_rotas(self):
        visitante = self.client.get("/admin?visao=dashboard")
        self.assertEqual(visitante.status_code, 302)
        self.assertEqual(visitante.headers["Location"], "/")

        self.autenticar_sessao(self.comprador_id)
        usuario = self.client.get("/admin?visao=dashboard")
        self.assertEqual(usuario.status_code, 302)
        self.assertEqual(usuario.headers["Location"], "/")

        self.autenticar_sessao(self.admin_id, admin=True)
        dashboard = self.client.get("/admin?visao=dashboard")
        painel = self.client.get("/admin")
        html_dashboard = dashboard.data.decode("utf-8")
        conteudo_dashboard = html_dashboard.split('id="dashboard-conteudo"', 1)[1]

        self.assertEqual(dashboard.status_code, 200)
        self.assertIn('<body class="mds-dashboard">', html_dashboard)
        self.assertEqual(html_dashboard.count("<h1"), 1)
        self.assertIn("Dashboard Executivo", html_dashboard)
        self.assertIn("Dados somente de leitura", html_dashboard)
        self.assertNotIn("<form", conteudo_dashboard)
        self.assertIn("Painel admin".encode(), painel.data)
        self.assertNotIn(b'class="dashboard-shell"', painel.data)
        self.assertNotIn(
            "/dashboard", {regra.rule for regra in app.url_map.iter_rules()}
        )

    def test_dashboard_exibe_metricas_atividade_marketplace_e_sistema_sem_escrita(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "UPDATE usuarios SET loja_nome=?, loja_bairro=? WHERE id=?",
                ("Loja da Ponte", "Centro", self.vendedor_id),
            )
            db.execute(
                "INSERT INTO anuncios "
                "(usuario_id, titulo, descricao, preco, categoria, condicao) "
                "VALUES (?,?,?,?,?,?)",
                (
                    self.vendedor_id,
                    "Notebook para trabalho",
                    "Equipamento revisado",
                    "2.500,00",
                    "Eletronicos",
                    "Usado",
                ),
            )
            db.execute(
                "INSERT INTO pedidos "
                "(anuncio_id, comprador_id, vendedor_id, valor, status) "
                "VALUES (?,?,?,?,?)",
                (
                    self.anuncio_id,
                    self.comprador_id,
                    self.vendedor_id,
                    "1.200,00",
                    "aguardando",
                ),
            )
            db.commit()
            antes = tuple(
                db.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
                for tabela in ("usuarios", "anuncios", "pedidos")
            )

        self.autenticar_sessao(self.admin_id, admin=True)
        ambiente = {
            "RENDER": "true",
            "RENDER_GIT_COMMIT": "abcdef1234567890abcdef1234567890abcdef12",
            "RENDER_DEPLOY_ID": "dep-teste-009",
            "CI_STATUS": "success",
            "CI_TEST_COUNT": "88",
        }
        with patch.dict(os.environ, ambiente, clear=False):
            pagina = self.client.get("/admin?visao=dashboard")
        html = pagina.data.decode("utf-8")

        with app.app_context():
            db = get_db()
            depois = tuple(
                db.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
                for tabela in ("usuarios", "anuncios", "pedidos")
            )

        self.assertEqual(pagina.status_code, 200)
        self.assertEqual(antes, depois)
        for indicador, valor in (
            ("usuarios_cadastrados", 3),
            ("lojas_cadastradas", 1),
            ("anuncios_ativos", 2),
            ("pedidos", 1),
            ("solicitacoes_compra", 1),
        ):
            self.assertIn(
                f'data-dashboard-metric="{indicador}" data-value="{valor}"', html
            )
        for texto in (
            "Bicicleta aro 29",
            "Notebook para trabalho",
            "Loja da Ponte",
            "Centro",
            'data-category="Eletrônicos" data-value="1"',
            "dep-teste-009",
            "abcdef123456",
            "Aprovado",
            ">88<",
            "HTTP 200",
        ):
            self.assertIn(texto, html)
        for titulo in (
            "dashboard-overview-title",
            "dashboard-activity-title",
            "dashboard-market-title",
            "dashboard-system-title",
        ):
            self.assertIn(f'aria-labelledby="{titulo}"', html)

        with open(
            os.path.join(app.root_path, "static", "styles.css"), encoding="utf-8"
        ) as arquivo_css:
            css = arquivo_css.read()
        self.assertIn(".mds-dashboard", css)
        self.assertIn(".dashboard-market-grid", css)
        self.assertIn("@media(max-width:639px)", css)

    def test_pagina_produto_aplica_mds_premium_e_cta_principal(self):
        pagina = self.client.get(f"/anuncio/{self.anuncio_id}")
        html = pagina.data.decode("utf-8")

        self.assertEqual(pagina.status_code, 200)
        self.assertIn('<body class="mds-product">', html)
        self.assertEqual(html.count("<h1"), 1)
        self.assertIn('class="product-premium"', html)
        self.assertIn('aria-label="Fotos do produto"', html)
        self.assertIn('aria-label="Informações principais do produto"', html)
        self.assertIn('class="btn product-primary-action"', html)
        self.assertIn("Entrar para solicitar compra", html)
        self.assertIn('aria-label="Etapas da compra"', html)
        self.assertIn(f'href="/comprar/{self.anuncio_id}"', html)
        self.assertIn(f'href="/anuncio/{self.anuncio_id}/contato"', html)
        self.assertIn("Compartilhar produto", html)
        self.assertIn(
            f'data-share-url="http://localhost/anuncio/{self.anuncio_id}"', html
        )
        self.assertIn('data-share-action="whatsapp-business"', html)
        self.assertIn('data-share-action="native"', html)
        self.assertIn('data-share-action="copy"', html)
        self.assertIn(
            f'<link rel="canonical" href="http://localhost/anuncio/{self.anuncio_id}">',
            html,
        )

        marcadores = (
            'class="product-intro"',
            'class="product-gallery',
            'class="product-purchase-panel"',
            'class="product-details-layout"',
        )
        posicoes = [html.index(marcador) for marcador in marcadores]
        self.assertEqual(posicoes, sorted(posicoes))

        with open(
            os.path.join(app.root_path, "static", "styles.css"), encoding="utf-8"
        ) as arquivo_css:
            css = arquivo_css.read()
        for estado in (
            ".product-primary-action:hover",
            ".product-primary-action:active",
            ".product-primary-action:disabled",
            ".product-primary-action:focus-visible",
        ):
            self.assertIn(estado, css)

    def test_dono_visualiza_cta_de_compra_desabilitado_com_motivo(self):
        self.autenticar_sessao(self.vendedor_id)
        pagina = self.client.get(f"/anuncio/{self.anuncio_id}")
        html = pagina.data.decode("utf-8")

        self.assertEqual(pagina.status_code, 200)
        self.assertIn("product-primary-action", html)
        self.assertIn("disabled", html)
        self.assertIn('aria-describedby="purchase-owner-help"', html)
        self.assertIn("Você administra este anúncio", html)
        self.assertIn("Contas administradoras não podem comprar", html)

    def test_fluxo_compra_explica_etapas_e_proximo_passo(self):
        self.autenticar_sessao(self.comprador_id)
        checkout = self.client.get(f"/comprar/{self.anuncio_id}")
        html_checkout = checkout.data.decode("utf-8")

        self.assertEqual(checkout.status_code, 200)
        self.assertIn('aria-label="Progresso da compra"', html_checkout)
        self.assertIn("Solicitação", html_checkout)
        self.assertIn("Resposta do vendedor", html_checkout)
        self.assertIn("Entrega e pagamento", html_checkout)
        self.assertIn("Nenhum pagamento será cobrado agora", html_checkout)

        self.criar_pedido_de_teste()
        compras = self.client.get("/pedidos").data.decode("utf-8")
        self.assertIn("aguarde o vendedor confirmar a disponibilidade", compras)

        self.autenticar_sessao(self.vendedor_id)
        vendas = self.client.get("/pedidos").data.decode("utf-8")
        self.assertIn("confirme a disponibilidade ou recuse o pedido", vendas)
        self.assertIn('data-notification-count="1"', vendas)
        self.assertIn("Novo pedido recebido", vendas)

    def test_central_cria_lista_e_conta_notificacao_de_novo_pedido(self):
        pedido_id = self.criar_pedido_de_teste()
        self.autenticar_sessao(self.vendedor_id)

        pagina = self.client.get("/").data.decode("utf-8")
        self.assertIn('data-notification-count="1"', pagina)
        self.assertIn("Central de Notificações", pagina)
        self.assertIn("Novo pedido recebido", pagina)
        self.assertIn("Comprador solicitou Bicicleta aro 29", pagina)

        with app.app_context():
            db = get_db()
            notificacao = db.execute(
                "SELECT * FROM notifications WHERE usuario_id=?",
                (self.vendedor_id,),
            ).fetchone()
            self.assertEqual(notificacao["tipo"], "NOVO_PEDIDO")
            self.assertEqual(notificacao["status"], "nao_lida")
            self.assertEqual(notificacao["referencia_tipo"], "pedido")
            self.assertEqual(notificacao["referencia_id"], pedido_id)
            self.assertEqual(notificacao["url"], f"/pedidos#pedido-{pedido_id}")
            self.assertEqual(
                db.execute(
                    "SELECT COUNT(*) FROM notifications WHERE usuario_id=?",
                    (self.comprador_id,),
                ).fetchone()[0],
                0,
            )

    def test_notificacao_pode_ser_aberta_e_marcada_como_lida(self):
        pedido_id = self.criar_pedido_de_teste()
        with app.app_context():
            notificacao_id = (
                get_db()
                .execute(
                    "SELECT id FROM notifications WHERE usuario_id=?",
                    (self.vendedor_id,),
                )
                .fetchone()[0]
            )
        self.autenticar_sessao(self.vendedor_id)

        resposta = self.client.post(
            f"/notificacoes/{notificacao_id}/abrir",
            data={"csrf_token": "token-teste"},
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta.headers["Location"].endswith(f"#pedido-{pedido_id}"))
        with app.app_context():
            notificacao = (
                get_db()
                .execute(
                    "SELECT status, lida_em FROM notifications WHERE id=?",
                    (notificacao_id,),
                )
                .fetchone()
            )
            self.assertEqual(notificacao["status"], "lida")
            self.assertIsNotNone(notificacao["lida_em"])

    def test_usuario_nao_acessa_notificacao_de_outra_pessoa(self):
        self.criar_pedido_de_teste()
        with app.app_context():
            notificacao_id = (
                get_db()
                .execute(
                    "SELECT id FROM notifications WHERE usuario_id=?",
                    (self.vendedor_id,),
                )
                .fetchone()[0]
            )
        self.autenticar_sessao(self.comprador_id)

        resposta = self.client.post(
            f"/notificacoes/{notificacao_id}/abrir",
            data={"csrf_token": "token-teste"},
        )
        self.assertEqual(resposta.status_code, 404)
        with app.app_context():
            status = (
                get_db()
                .execute(
                    "SELECT status FROM notifications WHERE id=?", (notificacao_id,)
                )
                .fetchone()[0]
            )
            self.assertEqual(status, "nao_lida")

    def test_marcar_todas_como_lidas_e_arquivar(self):
        self.criar_pedido_de_teste()
        with app.app_context():
            notificacao_id = (
                get_db()
                .execute(
                    "SELECT id FROM notifications WHERE usuario_id=?",
                    (self.vendedor_id,),
                )
                .fetchone()[0]
            )
        self.autenticar_sessao(self.vendedor_id)

        resposta = self.client.post(
            "/notificacoes/ler-todas",
            data={"csrf_token": "token-teste", "retorno": "/notificacoes"},
        )
        self.assertEqual(resposta.headers["Location"], "/notificacoes")
        resposta = self.client.post(
            f"/notificacoes/{notificacao_id}/arquivar",
            data={"csrf_token": "token-teste"},
        )
        self.assertEqual(resposta.status_code, 302)
        with app.app_context():
            item = (
                get_db()
                .execute(
                    "SELECT status, lida_em, arquivada_em FROM notifications WHERE id=?",
                    (notificacao_id,),
                )
                .fetchone()
            )
            self.assertEqual(item["status"], "arquivada")
            self.assertIsNotNone(item["lida_em"])
            self.assertIsNotNone(item["arquivada_em"])

    def test_admin_tem_visao_agregada_sem_perder_isolamento(self):
        self.criar_pedido_de_teste()
        self.autenticar_sessao(self.admin_id, admin=True)

        pagina = self.client.get("/notificacoes")
        html = pagina.get_data(as_text=True)
        self.assertEqual(pagina.status_code, 200)
        self.assertIn("Visão administrativa", html)
        self.assertIn("Dados agregados", html)
        self.assertIn("Usuários alcançados", html)

    def test_central_possui_componente_unico_responsivo_e_acessivel(self):
        self.autenticar_sessao(self.vendedor_id)
        pagina = self.client.get("/").get_data(as_text=True)
        self.assertEqual(pagina.count("data-notification-center"), 1)
        self.assertIn('aria-label="Abrir Central de Notificações', pagina)
        self.assertIn("notification-center.js", pagina)

        with open(
            os.path.join(app.root_path, "static", "styles.css"), encoding="utf-8"
        ) as arquivo_css:
            css = arquivo_css.read()
        self.assertIn(".notification-panel", css)
        self.assertIn("@media(max-width:839px)", css)
        self.assertIn("@media(max-width:639px)", css)
        self.assertIn("@media(max-width:359px)", css)

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

    def test_cadastro_concede_selo_de_fundador_automaticamente(self):
        with self.client.session_transaction() as sessao:
            sessao["_csrf_token"] = "token-teste"
        resposta = self.client.post(
            "/cadastro",
            data={
                "csrf_token": "token-teste",
                "nome": "Fundadora Automática",
                "username": "fundadora_auto",
                "senha": "senha-segura",
                "whatsapp": "27999999994",
                "aceite_termos": "1",
            },
        )

        self.assertEqual(resposta.status_code, 302)
        with app.app_context():
            usuario = (
                get_db()
                .execute(
                    "SELECT fundador, fundador_desde, fundador_origem, "
                    "fundador_beneficios FROM usuarios WHERE username=?",
                    ("fundadora_auto",),
                )
                .fetchone()
            )
        self.assertEqual(usuario["fundador"], 1)
        self.assertIsNotNone(usuario["fundador_desde"])
        self.assertEqual(usuario["fundador_origem"], "automatico")
        self.assertEqual(usuario["fundador_beneficios"], "{}")

    def test_limite_impede_novos_selos_automaticos(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "UPDATE usuarios SET fundador=1, fundador_desde=CURRENT_TIMESTAMP, "
                "fundador_origem='automatico' WHERE id=?",
                (self.vendedor_id,),
            )
            db.commit()
        with self.client.session_transaction() as sessao:
            sessao["_csrf_token"] = "token-teste"

        with patch.object(app_module, "LIMITE_FUNDADORES", 1):
            resposta = self.client.post(
                "/cadastro",
                data={
                    "csrf_token": "token-teste",
                    "nome": "Pessoa sem Selo",
                    "username": "sem_selo",
                    "senha": "senha-segura",
                    "whatsapp": "27999999995",
                    "aceite_termos": "1",
                },
            )

        self.assertEqual(resposta.status_code, 302)
        with app.app_context():
            usuario = (
                get_db()
                .execute(
                    "SELECT fundador, fundador_desde, fundador_origem, "
                    "fundador_removido_em FROM usuarios "
                    "WHERE username=?",
                    ("sem_selo",),
                )
                .fetchone()
            )
        self.assertEqual(usuario["fundador"], 0)
        self.assertIsNone(usuario["fundador_desde"])
        self.assertIsNone(usuario["fundador_origem"])

    def test_migracao_incorpora_primeiros_usuarios_sem_ultrapassar_limite(self):
        with (
            app.app_context(),
            patch.dict(os.environ, {"FOUNDERS_LIMIT": "2"}, clear=False),
        ):
            db = get_db()
            db.execute(
                "UPDATE usuarios SET fundador=0, fundador_desde=NULL, "
                "fundador_origem=NULL, fundador_removido_em=NULL"
            )
            _backfill_fundadores(db)
            db.commit()
            usuarios = db.execute(
                "SELECT id, fundador, fundador_origem FROM usuarios "
                "ORDER BY criado_em ASC, id ASC"
            ).fetchall()

        self.assertEqual([usuario["fundador"] for usuario in usuarios], [1, 1, 0])
        self.assertEqual(usuarios[0]["fundador_origem"], "automatico")
        self.assertEqual(usuarios[1]["fundador_origem"], "automatico")
        self.assertIsNone(usuarios[2]["fundador_origem"])

    def test_admin_concede_remove_lista_e_filtra_fundadores(self):
        self.autenticar_sessao(self.admin_id, admin=True)
        conceder = self.client.post(
            f"/admin/usuario/{self.vendedor_id}/fundador",
            data={"csrf_token": "token-teste", "acao": "conceder"},
        )
        self.assertEqual(conceder.status_code, 302)
        with app.app_context():
            usuario = (
                get_db()
                .execute(
                    "SELECT fundador, fundador_origem, fundador_alterado_por "
                    "FROM usuarios WHERE id=?",
                    (self.vendedor_id,),
                )
                .fetchone()
            )
        self.assertEqual(usuario["fundador"], 1)
        self.assertEqual(usuario["fundador_origem"], "manual")
        self.assertEqual(usuario["fundador_alterado_por"], self.admin_id)

        painel = self.client.get("/admin?usuarios_filtro=fundadores")
        self.assertIn("Fundadores do Mercado Colatina".encode(), painel.data)
        self.assertIn(b"usuarios_filtro=fundadores", painel.data)
        self.assertIn(b"Remover Fundador", painel.data)

        remover = self.client.post(
            f"/admin/usuario/{self.vendedor_id}/fundador",
            data={"csrf_token": "token-teste", "acao": "remover"},
        )
        self.assertEqual(remover.status_code, 302)
        with app.app_context():
            usuario = (
                get_db()
                .execute(
                    "SELECT fundador, fundador_desde, fundador_origem, "
                    "fundador_removido_em FROM usuarios WHERE id=?",
                    (self.vendedor_id,),
                )
                .fetchone()
            )
        self.assertEqual(usuario["fundador"], 0)
        self.assertIsNotNone(usuario["fundador_desde"])
        self.assertEqual(usuario["fundador_origem"], "manual")
        self.assertIsNotNone(usuario["fundador_removido_em"])

    def test_usuario_comum_nao_pode_alterar_selo_de_fundador(self):
        self.autenticar_sessao(self.comprador_id)
        resposta = self.client.post(
            f"/admin/usuario/{self.vendedor_id}/fundador",
            data={"csrf_token": "token-teste", "acao": "conceder"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta.headers["Location"].endswith("/"))
        with app.app_context():
            fundador = (
                get_db()
                .execute(
                    "SELECT fundador FROM usuarios WHERE id=?", (self.vendedor_id,)
                )
                .fetchone()[0]
            )
        self.assertEqual(fundador, 0)

    def test_selo_de_fundador_aparece_na_loja_painel_e_perfil(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "UPDATE usuarios SET fundador=1, fundador_desde=CURRENT_TIMESTAMP, "
                "fundador_origem='automatico' WHERE id=?",
                (self.vendedor_id,),
            )
            db.commit()
        caminho_loja = self.preparar_loja_publica()

        pagina_loja = self.client.get(caminho_loja)
        self.assertIn("🏅 Fundador do Mercado Colatina".encode(), pagina_loja.data)

        self.autenticar_sessao(self.vendedor_id)
        painel = self.client.get("/painel-vendedor")
        conta = self.client.get("/minha-conta")
        self.assertIn("🏅 Fundador do Mercado Colatina".encode(), painel.data)
        self.assertIn("🏅 Fundador do Mercado Colatina".encode(), conta.data)

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
                for linha in get_db()
                .execute(
                    "SELECT tipo FROM pedido_eventos WHERE pedido_id=? ORDER BY id",
                    (pedido_id,),
                )
                .fetchall()
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
                (
                    "aguardando",
                    None,
                    None,
                    "2026-02-01 10:00:00",
                    "2026-02-01 10:00:00",
                ),
                (
                    "confirmado",
                    "2026-02-02 12:00:00",
                    None,
                    "2026-02-02 10:00:00",
                    "2026-02-02 12:00:00",
                ),
                (
                    "em_analise",
                    None,
                    None,
                    "2026-02-03 10:00:00",
                    "2026-02-03 13:00:00",
                ),
                (
                    "concluido",
                    "2026-02-05 10:00:00",
                    "2026-02-05 10:00:00",
                    "2026-02-04 10:00:00",
                    "2026-02-05 10:00:00",
                ),
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
            perfil = (
                get_db()
                .execute(
                    "SELECT loja_nome, loja_descricao, loja_bairro, loja_whatsapp "
                    "FROM usuarios WHERE id=?",
                    (self.vendedor_id,),
                )
                .fetchone()
            )
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
            nome = (
                get_db()
                .execute(
                    "SELECT loja_nome FROM usuarios WHERE id=?", (self.vendedor_id,)
                )
                .fetchone()[0]
            )
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
            perfil = (
                get_db()
                .execute(
                    "SELECT loja_nome, loja_descricao, loja_whatsapp FROM usuarios WHERE id=?",
                    (self.vendedor_id,),
                )
                .fetchone()
            )
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
            perfil = (
                get_db()
                .execute(
                    "SELECT loja_descricao FROM usuarios WHERE id=?",
                    (self.vendedor_id,),
                )
                .fetchone()
            )
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
        mais_vistos = self.client.get(
            "/painel-vendedor?filtro=mais_vistos"
        ).data.decode("utf-8")
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
                "preco='1.200,00', categoria='Outros', visualizacoes=9, "
                "criado_em='2026-01-01 10:00:00' WHERE id=?",
                (self.anuncio_id,),
            )
            db.execute(
                "INSERT INTO anuncios "
                "(usuario_id, titulo, descricao, preco, categoria, condicao, estoque, "
                "ativo, visualizacoes, criado_em) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    self.vendedor_id,
                    "Anúncio mais recente",
                    "Produto ativo da loja.",
                    "250,00",
                    "Eletrônicos",
                    "Novo",
                    2,
                    1,
                    3,
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
        self.assertIn("Visualizações dos anúncios</span><strong>12", html)
        self.assertLess(
            html.index("Anúncio mais recente"), html.index("Anúncio mais antigo")
        )
        self.assertNotIn("Anúncio privado pausado", html)

    def test_loja_publica_filtra_busca_categoria_preco_e_ordenacao(self):
        caminho = self.preparar_loja_publica()

        busca = self.client.get(f"{caminho}?q=mais+recente").data.decode("utf-8")
        self.assertIn("Anúncio mais recente", busca)
        self.assertNotIn("Anúncio mais antigo", busca)

        categoria = self.client.get(
            f"{caminho}?categoria=Eletr%C3%B4nicos"
        ).data.decode("utf-8")
        self.assertIn("Anúncio mais recente", categoria)
        self.assertNotIn("Anúncio mais antigo", categoria)

        faixa = self.client.get(f"{caminho}?preco_min=200&preco_max=300").data.decode(
            "utf-8"
        )
        self.assertIn("Anúncio mais recente", faixa)
        self.assertNotIn("Anúncio mais antigo", faixa)

        mais_vistos = self.client.get(f"{caminho}?ordem=mais_vistos").data.decode(
            "utf-8"
        )
        self.assertLess(
            mais_vistos.index("Anúncio mais antigo"),
            mais_vistos.index("Anúncio mais recente"),
        )

        menor_preco = self.client.get(f"{caminho}?ordem=menor_preco").data.decode(
            "utf-8"
        )
        self.assertLess(
            menor_preco.index("Anúncio mais recente"),
            menor_preco.index("Anúncio mais antigo"),
        )

        maior_preco = self.client.get(f"{caminho}?ordem=maior_preco").data.decode(
            "utf-8"
        )
        self.assertLess(
            maior_preco.index("Anúncio mais antigo"),
            maior_preco.index("Anúncio mais recente"),
        )
        self.assertIn("Limpar filtros", maior_preco)
        self.assertNotIn("Anúncio privado pausado", maior_preco)

    def test_loja_publica_usa_slug_canonico_e_atalho_por_id(self):
        caminho = self.preparar_loja_publica()
        slug_incorreto = self.client.get(f"/loja/{self.vendedor_id}-nome-antigo")
        somente_id = self.client.get(f"/loja/{self.vendedor_id}")

        self.assertEqual(slug_incorreto.status_code, 301)
        self.assertTrue(slug_incorreto.headers["Location"].endswith(caminho))
        self.assertEqual(somente_id.status_code, 301)
        self.assertTrue(somente_id.headers["Location"].endswith(caminho))
        self.assertEqual(
            app_module.slug_loja("Pedal Ágil Colatina"), "pedal-agil-colatina"
        )

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

        self.assertIn(
            "<title>Pedal Ágil Colatina | Loja no Mercado Colatina</title>", html
        )
        self.assertIn(
            'property="og:title" content="Pedal Ágil Colatina | Mercado Colatina"', html
        )
        self.assertIn('property="og:image"', html)
        self.assertIn("mercado-colatina-social.svg", html)
        self.assertIn(f'data-share-url="http://localhost{caminho}"', html)
        self.assertIn(f'<link rel="canonical" href="http://localhost{caminho}">', html)
        self.assertIn("store-share.js", html)
        self.assertIn("Compartilhar loja", html)
        self.assertIn('data-share-action="whatsapp-business"', html)
        self.assertIn('data-share-action="copy"', html)

    def test_visitante_acessa_loja_antes_de_abrir_anuncio(self):
        caminho = self.preparar_loja_publica()
        pagina_inicial = self.client.get("/")
        self.assertEqual(pagina_inicial.status_code, 200)
        self.assertIn(f'href="{caminho}">Abrir loja</a>'.encode(), pagina_inicial.data)

    def test_loja_inexistente_ou_inativa_retorna_404(self):
        self.assertEqual(
            self.client.get("/loja/999999-loja-inexistente").status_code, 404
        )
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
        self.assertIn("@media(max-width:640px){.public-store-cover", css)
        self.assertIn(
            ".public-store-page{display:grid;gap:30px;min-width:0;max-width:100%", css
        )
        self.assertIn(".public-store-filters{grid-template-columns:1fr", css)

    def test_sitemap_inclui_loja_publica_com_anuncio_ativo(self):
        caminho = self.preparar_loja_publica()
        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertIn(f"http://localhost{caminho}".encode(), sitemap.data)

    def preparar_dados_reputacao(self):
        with app.app_context():
            db = get_db()
            pedidos = (
                (
                    "concluido",
                    "2026-03-01 10:00:00",
                    "2026-03-02 10:00:00",
                    "2026-03-01 22:00:00",
                ),
                (
                    "concluido",
                    "2026-03-03 10:00:00",
                    "2026-03-05 10:00:00",
                    "2026-03-04 10:00:00",
                ),
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
        for privado in (
            "Último acesso",
            "Pedidos cancelados",
            "Pedidos em análise",
            "Tempo médio",
        ):
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
            verificada = (
                get_db()
                .execute(
                    "SELECT loja_verificada FROM usuarios WHERE id=?",
                    (self.vendedor_id,),
                )
                .fetchone()[0]
            )
            pedidos = (
                get_db()
                .execute(
                    "SELECT COUNT(*) FROM pedidos WHERE vendedor_id=?",
                    (self.vendedor_id,),
                )
                .fetchone()[0]
            )
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
            antes = (
                get_db()
                .execute(
                    "SELECT ultimo_acesso_em FROM usuarios WHERE id=?",
                    (self.vendedor_id,),
                )
                .fetchone()[0]
            )
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
            depois = (
                get_db()
                .execute(
                    "SELECT ultimo_acesso_em FROM usuarios WHERE id=?",
                    (self.vendedor_id,),
                )
                .fetchone()[0]
            )
        self.assertIsNotNone(depois)

    def test_criacao_do_pedido_gera_evento_inicial(self):
        pedido_id = self.criar_pedido_de_teste()
        with app.app_context():
            evento = (
                get_db()
                .execute(
                    "SELECT * FROM pedido_eventos WHERE pedido_id=? AND tipo='PEDIDO_CRIADO'",
                    (pedido_id,),
                )
                .fetchone()
            )
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
            evento_sistema = (
                get_db()
                .execute(
                    "SELECT papel_usuario FROM pedido_eventos "
                    "WHERE pedido_id=? AND tipo='ESTOQUE_RESERVADO'",
                    (pedido_id,),
                )
                .fetchone()
            )
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
            conclusao = (
                get_db()
                .execute(
                    "SELECT papel_usuario FROM pedido_eventos "
                    "WHERE pedido_id=? AND tipo='PEDIDO_CONCLUIDO'",
                    (pedido_id,),
                )
                .fetchone()
            )
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
            pedido = (
                get_db()
                .execute(
                    "SELECT status, vendedor_confirmou_em, comprador_confirmou_em FROM pedidos WHERE id=?",
                    (pedido_id,),
                )
                .fetchone()
            )
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
            anuncio = (
                get_db()
                .execute(
                    "SELECT estoque, ativo FROM anuncios WHERE id=?", (self.anuncio_id,)
                )
                .fetchone()
            )
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
            anuncio = (
                get_db()
                .execute(
                    "SELECT estoque, ativo FROM anuncios WHERE id=?", (self.anuncio_id,)
                )
                .fetchone()
            )
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
                "FROM pedidos WHERE id=?",
                (pedido_id,),
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
            pedido = (
                get_db()
                .execute(
                    "SELECT status, problema_motivo FROM pedidos WHERE id=?",
                    (pedido_id,),
                )
                .fetchone()
            )
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
            estoque_antes = (
                get_db()
                .execute("SELECT estoque FROM anuncios WHERE id=?", (self.anuncio_id,))
                .fetchone()[0]
            )
        self.autenticar_sessao(self.comprador_id)
        self.client.post(
            f"/pedido/{pedido_id}/problema",
            data={"csrf_token": "token-teste", "motivo": "VENDEDOR_NAO_RESPONDE"},
        )
        with app.app_context():
            estoque_depois = (
                get_db()
                .execute("SELECT estoque FROM anuncios WHERE id=?", (self.anuncio_id,))
                .fetchone()[0]
            )
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
                (
                    "Pessoa alheia",
                    "alheio",
                    generate_password_hash("senha-segura"),
                    "27999999994",
                ),
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
            for tipo in (
                "VENDEDOR_CONFIRMOU",
                "ESTOQUE_RESERVADO",
                "VENDA_MARCADA_COMO_REALIZADA",
            ):
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
                (
                    self.anuncio_id,
                    self.comprador_id,
                    self.vendedor_id,
                    "1.200,00",
                    "aguardando",
                ),
            )
            pedido_id = db.execute("SELECT MAX(id) FROM pedidos").fetchone()[0]
            db.commit()
        init_db()
        self.assertEqual(self.tipos_eventos(pedido_id), ["PEDIDO_CRIADO"])
        with app.app_context():
            evento = (
                get_db()
                .execute(
                    "SELECT usuario_id, papel_usuario, dados_adicionais FROM pedido_eventos "
                    "WHERE pedido_id=?",
                    (pedido_id,),
                )
                .fetchone()
            )
            self.assertIsNone(evento["usuario_id"])
            self.assertEqual(evento["papel_usuario"], "sistema")
            self.assertIn('"legado":true', evento["dados_adicionais"])
        self.autenticar_sessao(self.vendedor_id)
        self.client.post(
            f"/pedido/{pedido_id}/confirmar", data={"csrf_token": "token-teste"}
        )
        with app.app_context():
            status = (
                get_db()
                .execute("SELECT status FROM pedidos WHERE id=?", (pedido_id,))
                .fetchone()[0]
            )
            self.assertEqual(status, "confirmado")

    def test_novo_pedido_dispara_email_administrativo_e_registra_envio(self):
        with patch.object(
            app_module, "enviar_alerta_novo_pedido", return_value="enviado"
        ) as enviar:
            pedido_id = self.criar_pedido_de_teste()

        enviar.assert_called_once()
        with app.app_context():
            pedido = (
                get_db()
                .execute(
                    "SELECT admin_email_status, admin_email_enviado_em FROM pedidos WHERE id=?",
                    (pedido_id,),
                )
                .fetchone()
            )
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
        with patch.object(
            app_module, "enviar_alerta_novo_pedido", return_value="falhou"
        ):
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
            pedido = (
                get_db()
                .execute(
                    "SELECT admin_email_status, admin_email_enviado_em FROM pedidos WHERE id=?",
                    (pedido_id,),
                )
                .fetchone()
            )
            self.assertEqual(pedido["admin_email_status"], "enviado")
            self.assertIsNotNone(pedido["admin_email_enviado_em"])

    def test_admin_exibe_texto_do_email_com_acentuacao_correta(self):
        self.autenticar_sessao(self.admin_id, admin=True)
        with patch.dict(os.environ, {"ADMIN_NOTIFICATION_EMAIL": "pelers@gmail.com"}):
            painel = self.client.get("/admin")

        self.assertIn(
            "Nenhum pedido aguardando atenção neste momento.".encode(), painel.data
        )
        self.assertIn(
            "o serviço remetente ainda precisa ser ativado.".encode(), painel.data
        )
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
            "/quem-somos",
            "/seja-parceiro",
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

    def test_home_exibe_ofertas_de_parceiros_com_monetizacao_transparente(self):
        pagina = self.client.get("/")

        self.assertEqual(pagina.status_code, 200)
        self.assertIn("Conteúdo de parceiros".encode(), pagina.data)
        self.assertIn("Ofertas de Parceiros".encode(), pagina.data)
        self.assertNotIn("Paulo Eler".encode(), pagina.data)
        self.assertIn("Algumas ofertas desta seção são exibidas".encode(), pagina.data)
        self.assertIn("Ver oferta".encode(), pagina.data)
        self.assertIn(b'loading="lazy"', pagina.data)
        self.assertIn(b'decoding="async"', pagina.data)
        self.assertIn(b"data-partner-carousel", pagina.data)
        self.assertIn(b"data-carousel-prev", pagina.data)
        self.assertIn(b"data-carousel-next", pagina.data)
        self.assertIn(b"partner-offers-carousel.js", pagina.data)
        self.assertIn(b'rel="sponsored noopener noreferrer"', pagina.data)
        self.assertIn(b'data-click-area="imagem"', pagina.data)
        self.assertIn(b'data-click-area="titulo"', pagina.data)
        self.assertIn(b'data-click-area="botao"', pagina.data)
        self.assertIn(b'target="_blank"', pagina.data)
        self.assertIn(
            b'data-responsive-layout="wide-6 desktop-5 tablet-3 mobile-2"',
            pagina.data,
        )
        html = pagina.data.decode("utf-8")
        self.assertEqual(html.count('class="partner-offer-card"'), 6)
        self.assertEqual(html.count('data-link-source="official"'), 6)
        self.assertEqual(len(app_module.OFERTAS_PARCEIROS_HOME), 6)
        self.assertLess(
            html.index('id="ofertas"'), html.index('id="ofertas-parceiros"')
        )
        self.assertLess(html.index('id="ofertas-parceiros"'), html.index('id="planos"'))
        self.assertNotIn('id="achados"', html)

        caminho_carrossel = os.path.join(
            app_module.BASE_DIR, "static", "partner-offers-carousel.js"
        )
        with open(caminho_carrossel, encoding="utf-8") as arquivo_carrossel:
            javascript = arquivo_carrossel.read()
        self.assertIn('event.key !== "Enter"', javascript)
        self.assertIn('event.key === "ArrowLeft"', javascript)
        self.assertIn('event.key === "ArrowRight"', javascript)
        self.assertIn("window.setInterval", javascript)
        self.assertIn("prefersReducedMotion", javascript)
        self.assertIn('carousel.addEventListener("mouseenter", pause)', javascript)
        self.assertIn('carousel.addEventListener("focusin", pause)', javascript)
        self.assertIn("IntersectionObserver", javascript)
        self.assertIn("navigator.sendBeacon", javascript)
        self.assertIn('sendAnalytics(carousel, "click"', javascript)
        self.assertIn('sendAnalytics(carousel, "impression"', javascript)
        self.assertIn(
            b'data-analytics-endpoint="/analytics/afiliados/evento"', pagina.data
        )
        self.assertIn(b'data-affiliate-offer="celulares-acessorios"', pagina.data)

    def test_home_ofertas_de_parceiros_usam_links_individuais_por_card(self):
        ofertas = app_module.OFERTAS_PARCEIROS_HOME
        urls = [oferta["url"] for oferta in ofertas]

        self.assertEqual(len(ofertas), 6)
        self.assertTrue(all(urls))
        self.assertEqual(len(set(urls)), len(urls))

        pagina = self.client.get("/")
        html = pagina.data.decode("utf-8")

        for oferta in ofertas:
            self.assertIn(f'href="{oferta["url"]}"', html)
            self.assertIn(f'data-destino="{oferta["identificador_destino"]}"', html)
            self.assertIn(oferta["titulo"], html)
            self.assertIn(oferta["preco"], html)

    def test_configuracao_centralizada_usa_seis_links_oficiais_unicos(self):
        ofertas = build_partner_offers({})
        env_keys = [config["env_key"] for config in PARTNER_OFFERS_CONFIG]
        oficiais = [config["official_url"] for config in PARTNER_OFFERS_CONFIG]
        fallbacks = [config["fallback_url"] for config in PARTNER_OFFERS_CONFIG]
        imagens = [oferta["imagem"] for oferta in ofertas]

        self.assertEqual(len(ofertas), 6)
        self.assertEqual(len(set(env_keys)), 6)
        self.assertEqual(len(set(oficiais)), 6)
        self.assertEqual(len(set(fallbacks)), 6)
        self.assertTrue(all(oferta["url"] for oferta in ofertas))
        self.assertTrue(all(url.startswith("https://meli.la/") for url in oficiais))
        self.assertTrue(all(oferta["link_oficial_configurado"] for oferta in ofertas))
        self.assertEqual([oferta["url"] for oferta in ofertas], oficiais)
        self.assertEqual(len(set(imagens)), 6)
        self.assertTrue(all(imagem.endswith("-premium.webp") for imagem in imagens))

    def test_configuracao_centralizada_aceita_link_oficial_sem_alterar_valor(self):
        env_key = PARTNER_OFFERS_CONFIG[0]["env_key"]
        url_fornecida = "https://example.invalid/link-oficial-fornecido"
        ofertas = build_partner_offers({env_key: url_fornecida})

        self.assertEqual(ofertas[0]["url"], url_fornecida)
        self.assertTrue(ofertas[0]["link_oficial_configurado"])
        self.assertTrue(all(oferta["link_oficial_configurado"] for oferta in ofertas))

    def test_home_declara_configuracao_responsiva_dos_cards_parceiros(self):
        caminho_css = os.path.join(app_module.BASE_DIR, "static", "styles.css")
        with open(caminho_css, encoding="utf-8") as arquivo_css:
            css = arquivo_css.read()

        self.assertIn("calc((100% - 3.75rem) / 6)", css)
        self.assertIn("calc((100% - 3rem) / 5)", css)
        self.assertIn("calc((100% - 2rem) / 3)", css)
        self.assertIn("calc((100% - .75rem) / 2)", css)
        self.assertIn("@media(max-width:1399px)", css)
        self.assertIn("@media(max-width:1023px)", css)
        self.assertIn("@media(max-width:639px)", css)

    def test_home_oferta_parceira_mantem_mesma_url_na_imagem_titulo_e_botao(self):
        pagina = self.client.get("/")
        html = pagina.data.decode("utf-8")
        blocos = html.split('class="partner-offer-card"')[1:]

        self.assertEqual(len(blocos), 6)

        for oferta, bloco in zip(
            app_module.OFERTAS_PARCEIROS_HOME, blocos, strict=True
        ):
            url = oferta["url"]
            self.assertIn(f'href="{url}"', bloco)
            self.assertIn('data-click-area="imagem"', bloco)
            self.assertIn('data-click-area="titulo"', bloco)
            self.assertIn('data-click-area="botao"', bloco)
            self.assertEqual(bloco.count(f'href="{url}"'), 1)

    def test_analytics_registra_clique_unico_com_dados_validados_no_servidor(self):
        self.client.get("/")
        with self.client.session_transaction() as sessao:
            token = sessao["_csrf_token"]

        resposta = self.client.post(
            "/analytics/afiliados/evento",
            json={
                "csrf_token": token,
                "event_type": "click",
                "offer_id": "celulares-acessorios",
                "device": "desktop",
                "source": "origem-nao-confiavel",
            },
        )

        self.assertEqual(resposta.status_code, 204)
        with app.app_context():
            evento = get_db().execute("SELECT * FROM afiliado_eventos").fetchone()
        self.assertEqual(evento["parceiro"], "mercado_livre")
        self.assertEqual(evento["oferta_id"], "celulares-acessorios")
        self.assertEqual(evento["categoria"], "Celulares e acessórios")
        self.assertEqual(evento["tipo_evento"], "click")
        self.assertEqual(evento["origem"], "home")
        self.assertEqual(evento["dispositivo"], "desktop")
        self.assertIsNotNone(evento["ocorrido_em"])

    def test_analytics_conta_cliques_repetidos_e_dispositivos_separadamente(self):
        self.client.get("/")
        with self.client.session_transaction() as sessao:
            token = sessao["_csrf_token"]

        for device in ("desktop", "mobile", "mobile"):
            resposta = self.client.post(
                "/analytics/afiliados/evento",
                json={
                    "csrf_token": token,
                    "event_type": "click",
                    "offer_id": "fones-audio",
                    "device": device,
                },
            )
            self.assertEqual(resposta.status_code, 204)

        with app.app_context():
            linhas = (
                get_db()
                .execute(
                    "SELECT dispositivo, COUNT(*) AS total FROM afiliado_eventos "
                    "GROUP BY dispositivo ORDER BY dispositivo"
                )
                .fetchall()
            )
        self.assertEqual(
            [(linha["dispositivo"], linha["total"]) for linha in linhas],
            [("desktop", 1), ("mobile", 2)],
        )

    def test_analytics_rejeita_csrf_evento_categoria_e_dispositivo_invalidos(self):
        self.client.get("/")
        with self.client.session_transaction() as sessao:
            token = sessao["_csrf_token"]

        payloads = (
            {
                "event_type": "click",
                "offer_id": "celulares-acessorios",
                "device": "desktop",
            },
            {
                "csrf_token": token,
                "event_type": "compra",
                "offer_id": "celulares-acessorios",
                "device": "desktop",
            },
            {
                "csrf_token": token,
                "event_type": "click",
                "offer_id": "categoria-inexistente",
                "device": "desktop",
            },
            {
                "csrf_token": token,
                "event_type": "click",
                "offer_id": "celulares-acessorios",
                "device": "tablet",
            },
        )
        for payload in payloads:
            with self.subTest(payload=payload):
                self.assertEqual(
                    self.client.post(
                        "/analytics/afiliados/evento", json=payload
                    ).status_code,
                    400,
                )

        with app.app_context():
            total = (
                get_db().execute("SELECT COUNT(*) FROM afiliado_eventos").fetchone()[0]
            )
        self.assertEqual(total, 0)

    def test_dashboard_afiliados_e_exclusivo_do_admin_e_calcula_ranking_e_ctr(self):
        with app.app_context():
            db = get_db()
            dados = (
                ("celulares-acessorios", "Celulares e acessórios", "click", 3),
                ("celulares-acessorios", "Celulares e acessórios", "impression", 6),
                ("fones-audio", "Fones e áudio", "click", 2),
                ("fones-audio", "Fones e áudio", "impression", 4),
                ("informatica", "Informática", "click", 1),
                ("informatica", "Informática", "impression", 4),
            )
            for offer_id, category, event_type, quantity in dados:
                for _ in range(quantity):
                    db.execute(
                        "INSERT INTO afiliado_eventos "
                        "(parceiro, oferta_id, categoria, tipo_evento, origem, dispositivo) "
                        "VALUES (?,?,?,?,?,?)",
                        (
                            "mercado_livre",
                            offer_id,
                            category,
                            event_type,
                            "home",
                            "desktop",
                        ),
                    )
            db.execute(
                "INSERT INTO afiliado_eventos "
                "(parceiro, oferta_id, categoria, tipo_evento, origem, dispositivo, ocorrido_em) "
                "VALUES (?,?,?,?,?,?,datetime('now', '-10 days'))",
                (
                    "mercado_livre",
                    "casa-utilidades",
                    "Casa e utilidades",
                    "click",
                    "home",
                    "mobile",
                ),
            )
            db.commit()

        visitante = self.client.get("/admin?visao=afiliados")
        self.assertEqual(visitante.status_code, 302)
        self.autenticar_sessao(self.comprador_id)
        usuario = self.client.get("/admin?visao=afiliados")
        self.assertEqual(usuario.status_code, 302)

        self.autenticar_sessao(self.admin_id, admin=True)
        pagina = self.client.get("/admin?visao=afiliados")
        html = pagina.data.decode("utf-8")
        self.assertEqual(pagina.status_code, 200)
        self.assertIn("Analytics de Afiliados", html)
        self.assertIn('data-affiliate-metric="today" data-value="6"', html)
        self.assertIn('data-affiliate-metric="7-days" data-value="6"', html)
        self.assertIn('data-affiliate-metric="30-days" data-value="7"', html)
        self.assertIn(
            'data-affiliate-ctr="celulares-acessorios" data-value="50.0"', html
        )
        self.assertIn('data-affiliate-ctr="fones-audio" data-value="50.0"', html)
        self.assertIn('data-affiliate-ctr="informatica" data-value="25.0"', html)
        self.assertLess(
            html.index('data-affiliate-category="celulares-acessorios"'),
            html.index('data-affiliate-category="fones-audio"'),
        )
        self.assertLess(
            html.index('data-affiliate-category="fones-audio"'),
            html.index('data-affiliate-category="informatica"'),
        )
        self.assertIn("TOP categoria", html)
        self.assertIn("Menor interesse", html)
        self.assertIn("Amazon · Magalu · Shopee", html)

    def test_dashboard_afiliados_sem_eventos_nao_inventa_interesse(self):
        self.autenticar_sessao(self.admin_id, admin=True)
        pagina = self.client.get("/admin?visao=afiliados")
        html = pagina.data.decode("utf-8")

        self.assertEqual(pagina.status_code, 200)
        self.assertGreaterEqual(html.count("Sem dados"), 2)
        self.assertIn('data-affiliate-metric="today" data-value="0"', html)
        self.assertIn(
            'data-affiliate-category="celulares-acessorios" data-clicks="0"', html
        )

    def test_plano_gratuito_permite_ate_dez_anuncios_ativos(self):
        with app.app_context():
            db = get_db()
            for numero in range(2, 11):
                db.execute(
                    "INSERT INTO anuncios "
                    "(usuario_id, titulo, descricao, preco, categoria, condicao, ativo, estoque) "
                    "VALUES (?,?,?,?,?,?,1,1)",
                    (
                        self.vendedor_id,
                        f"Produto gratuito {numero}",
                        "Anúncio para validar o limite gratuito.",
                        "10,00",
                        "Outros",
                        "Usado",
                    ),
                )
            db.commit()
            permitido, motivo = app_module.pode_criar_anuncio(self.vendedor_id)
            self.assertFalse(permitido)
            self.assertEqual(motivo, "limite")

            db.execute(
                "UPDATE anuncios SET ativo=0 WHERE usuario_id=? AND titulo=?",
                (self.vendedor_id, "Produto gratuito 10"),
            )
            db.commit()
            permitido, aviso = app_module.pode_criar_anuncio(self.vendedor_id)
            self.assertTrue(permitido)
            self.assertIn("1 anúncio(s) gratuito(s) restante(s)", aviso)

        pagina = self.client.get("/")
        self.assertIn("Até 10 anúncios ativos".encode(), pagina.data)

    def test_home_destaca_busca_compra_e_publicacao_no_hero_premium(self):
        pagina = self.client.get("/")

        self.assertEqual(pagina.status_code, 200)
        self.assertIn("Anunciar".encode(), pagina.data)
        self.assertIn("Comprar".encode(), pagina.data)
        self.assertIn(
            'class="home-premium-search home-official-search"'.encode(),
            pagina.data,
        )
        self.assertIn(b'href="/cadastro"', pagina.data)
        self.assertNotIn(b'class="hero-signup-promo"', pagina.data)
        self.assertNotIn(b'class="hero-panel"', pagina.data)
        self.assertIn(b"<summary>Compartilhar</summary>", pagina.data)
        self.assertIn(b'data-share-url="http://localhost/"', pagina.data)
        self.assertIn(b'data-share-action="whatsapp-business"', pagina.data)
        self.assertIn(b'data-share-action="copy"', pagina.data)
        self.assertIn(b'class="home-visit-proof"', pagina.data)
        self.assertIn(b"data-home-visits=", pagina.data)
        self.assertIn(b"ao site</span>", pagina.data)

        self.autenticar_sessao(self.comprador_id)
        pagina_autenticada = self.client.get("/")
        self.assertIn("Publicar anúncio".encode(), pagina_autenticada.data)
        self.assertIn(b'href="/criar"', pagina_autenticada.data)
        self.assertIn(b'href="#ofertas"', pagina_autenticada.data)

    def test_patch_ux_005c_prioriza_acoes_na_primeira_dobra(self):
        html = self.client.get("/").data.decode("utf-8")

        self.assertIn("ux005c-first-fold", html)
        self.assertIn("Comprar agora", html)
        self.assertIn("Anunciar grátis", html)
        self.assertIn("O que você procura?", html)
        self.assertIn('placeholder="Ex.: celular, sofá ou eletricista"', html)
        self.assertIn("Encontrar agora", html)
        self.assertIn('class="home-solver-strip"', html)
        self.assertIn('id="home-solver-title">Encontre Quem Resolve</h2>', html)
        self.assertIn('href="/encontre-quem-resolve"', html)
        self.assertIn("Descrever minha necessidade", html)
        self.assertIn("data-ux005c-categories", html)
        self.assertLess(
            html.index("data-ux005c-search"), html.index("home-solver-strip")
        )
        self.assertLess(
            html.index("home-solver-strip"), html.index("data-ux005c-categories")
        )
        self.assertLess(
            html.index("data-ux005c-categories"), html.index('id="ofertas"')
        )

        html_resultados = self.client.get("/?q=celular").data.decode("utf-8")
        self.assertNotIn('class="home-solver-strip"', html_resultados)

        self.autenticar_sessao(self.comprador_id)
        html_autenticado = self.client.get("/").data.decode("utf-8")
        self.assertIn("Publicar anúncio", html_autenticado)
        self.assertIn('class="btn btn-outline ux005c-secondary-cta"', html_autenticado)

    def test_patch_ux_006b_reforca_apenas_o_hero_da_home_compacta(self):
        with patch.object(app_module, "HOME_CIDADE_VIVA_ENABLED", True):
            html = self.client.get("/").data.decode("utf-8")

        self.assertIn(
            '<h1 id="hero-title"><span>O melhor da cidade,</span>'
            "<em>mais perto.</em></h1>",
            html,
        )
        self.assertLess(
            html.index('class="home-official-panorama"'),
            html.index("data-ux005c-search"),
        )
        self.assertIn("home-compact-ux006a", html)

        caminho_css = os.path.join(app.static_folder, "styles.css")
        with open(caminho_css, encoding="utf-8") as arquivo:
            css = arquivo.read()

        self.assertIn("/* PATCH UX-006B", css)
        self.assertIn("width:min(78%,84rem)", css)
        self.assertIn("white-space:nowrap", css)
        self.assertIn(
            ".home-compact-ux006a .ux005c-first-fold .ux005c-primary-cta",
            css,
        )
        self.assertNotIn(".home-city-movement .ux005c-primary-cta", css)

    def test_patch_ux_006b_preserva_feature_flag_e_home_legada(self):
        with patch.object(app_module, "HOME_CIDADE_VIVA_ENABLED", False):
            html = self.client.get("/").data.decode("utf-8")

        self.assertNotIn("home-compact-ux006a", html)
        self.assertIn("ux005c-first-fold", html)
        self.assertIn("data-ux005c-search", html)
        self.assertIn('id="ofertas"', html)

    def test_compartilhamento_direciona_para_whatsapp_business(self):
        caminho_js = os.path.join(app.static_folder, "store-share.js")
        with open(caminho_js, encoding="utf-8") as arquivo:
            javascript = arquivo.read()

        self.assertIn("package=com.whatsapp.w4b", javascript)
        self.assertIn("https://web.whatsapp.com/send?text=", javascript)

    def test_home_aplica_mds_com_estrutura_semantica_e_acessivel(self):
        pagina = self.client.get("/")
        html = pagina.data.decode("utf-8")

        self.assertEqual(pagina.status_code, 200)
        self.assertIn('<body class="mds-home mx-home-premium home-official">', html)
        self.assertEqual(html.count("<h1"), 1)
        self.assertIn("<span>O melhor da cidade,</span><em>mais perto.</em>", html)
        self.assertIn('<label for="busca">Buscar produtos e serviços</label>', html)
        self.assertIn('<label for="categoria">Categoria</label>', html)
        self.assertIn('aria-label="Buscar no Mercado Colatina"', html)
        self.assertIn('class="home-category-card active"', html)
        self.assertIn('<h3 class="card-titulo">', html)
        self.assertIn('aria-label="Informações do anúncio"', html)
        self.assertIn("Ver produto", html)

    def test_home_premium_aplica_identidade_categorias_cta_e_rodape(self):
        html = self.client.get("/").data.decode("utf-8")

        self.assertIn("mercado-colatina-logo-v0.9.svg", html)
        self.assertIn('class="home-official-hero-stage"', html)
        self.assertIn('class="home-official-panorama"', html)
        self.assertIn("colatina-rio-doce-panorama-hvl.jpg", html)
        self.assertIn("CC BY 4.0", html)
        self.assertIn('class="home-category-grid"', html)
        self.assertEqual(html.count('class="home-category-card'), 10)
        self.assertIn('id="planos" class="home-seller-callout"', html)
        self.assertIn("Tem um negócio em Colatina?", html)
        self.assertIn('class="site-footer home-premium-footer"', html)
        self.assertIn("A praça digital para comprar, vender", html)

    def test_home_exibe_confianca_empresas_parceiras_e_planos_preparados(self):
        html = self.client.get("/").data.decode("utf-8")

        self.assertIn('id="confianca"', html)
        self.assertIn("Por que confiar no Mercado Colatina?", html)
        self.assertIn("Criado em Colatina", html)
        self.assertIn("Comércio local em primeiro lugar", html)
        self.assertIn("Negociação direta", html)
        self.assertIn("Publicidade transparente", html)
        self.assertIn("Em constante evolução", html)
        self.assertEqual(html.count("data-trust-item"), 5)
        self.assertIn('id="empresas-parceiras"', html)
        self.assertIn("Empresas que acreditam no comércio local.", html)
        self.assertEqual(html.count("data-partner-card"), 6)
        self.assertIn('data-partner-levels="local destaque premium"', html)
        self.assertEqual(len(app_module.LOCAL_PARTNERS_HOME), 6)
        self.assertEqual(
            {item["nivel"] for item in app_module.LOCAL_PARTNERS_HOME},
            {"local", "destaque", "premium"},
        )
        self.assertTrue(
            all(item["placeholder"] for item in app_module.LOCAL_PARTNERS_HOME)
        )

    def test_rodape_exibe_navegacao_institucional_da_sprint(self):
        html = self.client.get("/").data.decode("utf-8")

        for texto in (
            "Quem Somos",
            "Seja Parceiro",
            "Segurança",
            "Como Funciona",
            "Política de Privacidade",
            "Termos de Uso",
        ):
            self.assertIn(texto, html)
        self.assertIn('href="/quem-somos"', html)
        self.assertIn('href="/seja-parceiro"', html)

    def test_home_exibe_painel_diario_com_cinco_placeholders_reutilizaveis(self):
        html = self.client.get("/").data.decode("utf-8")

        self.assertIn('id="hoje-em-colatina"', html)
        self.assertIn("Hoje em Colatina", html)
        self.assertIn("Informações essenciais da cidade", html)
        for titulo in (
            "Tempo",
            "Eventos",
            "Empregos",
            "Farmácia de Plantão",
            "Avisos",
        ):
            self.assertIn(titulo, html)
        self.assertEqual(html.count("data-daily-city-card"), 5)
        self.assertEqual(html.count("Em preparação"), 5)
        self.assertEqual(len(app_module.DAILY_CITY_CARDS), 5)
        self.assertTrue(
            all(item["placeholder"] for item in app_module.DAILY_CITY_CARDS)
        )
        self.assertEqual(
            {item["id"] for item in app_module.DAILY_CITY_CARDS},
            {"tempo", "eventos", "empregos", "farmacia-plantao", "avisos"},
        )

    def test_home_apresenta_blocos_na_ordem_home_first(self):
        html = self.client.get("/").data.decode("utf-8")
        marcadores = (
            'class="home-premium-hero',
            'class="home-category-section"',
            'id="ofertas"',
            'id="ofertas-parceiros"',
            'id="planos"',
            'id="home-stores-title"',
            'id="confianca"',
            'id="empresas-parceiras"',
            'id="hoje-em-colatina"',
            'id="acessar-pelo-celular"',
            'id="como-funciona"',
        )
        posicoes = [html.index(marcador) for marcador in marcadores]
        self.assertEqual(posicoes, sorted(posicoes))

    def test_cidade_viva_fica_desativada_por_padrao_e_preserva_home_anterior(self):
        html = self.client.get("/").data.decode("utf-8")

        self.assertFalse(app_module.HOME_CIDADE_VIVA_ENABLED)
        self.assertIn('<body class="mds-home mx-home-premium home-official">', html)
        self.assertNotIn("home-city-alive", html)
        self.assertNotIn("Cidade Viva", html)
        self.assertNotIn("data-home-city-recent", html)
        self.assertIn('id="confianca"', html)
        self.assertIn('id="hoje-em-colatina"', html)

    def test_cidade_viva_limita_vitrine_e_exibe_dados_reais_sem_inventar_metricas(self):
        with app.app_context():
            db = get_db()
            for indice in range(2, 8):
                db.execute(
                    "INSERT INTO anuncios "
                    "(usuario_id, titulo, descricao, preco, categoria, condicao, "
                    "ativo, estoque) VALUES (?,?,?,?,?,?,1,1)",
                    (
                        self.vendedor_id,
                        f"Produto Cidade Viva {indice}",
                        "Produto real usado no teste da composiÃ§Ã£o.",
                        f"{indice}0,00",
                        "Outros",
                        "Usado",
                    ),
                )
            db.execute(
                "INSERT INTO pedidos_servico "
                "(problema, categoria, bairro, urgencia, whatsapp, status) "
                "VALUES (?,?,?,?,?,'aberto')",
                (
                    "Preciso consertar uma tomada residencial",
                    "Casa e manutenÃ§Ã£o",
                    "Centro",
                    "semana",
                    "5527999999999",
                ),
            )
            db.commit()

        with (
            patch.object(app_module, "HOME_CIDADE_VIVA_ENABLED", True),
            patch.object(app_module, "HOME_CIDADE_VIVA_PRODUCT_LIMIT", 4),
        ):
            html = self.client.get("/").data.decode("utf-8")

        self.assertIn("home-city-alive", html)
        self.assertIn("home-compact-ux006a", html)
        self.assertIn("Cidade Viva", html)
        self.assertIn('data-city-metric="anuncios"', html)
        self.assertIn('data-city-metric="empresas"', html)
        self.assertIn('data-city-metric="necessidades"', html)
        self.assertIn("4 de 7 resultados", html)
        self.assertIn("Ver todos", html)
        self.assertEqual(html.count('class="card home-product-card"'), 4)
        self.assertEqual(html.count('class="home-city-recent-card"'), 3)
        self.assertNotIn("usuÃ¡rios online", html.lower())
        self.assertNotIn("movimentaÃ§Ã£o estimada", html.lower())

    def test_cidade_viva_ver_todos_restaura_composicao_integral_da_home(self):
        with app.app_context():
            db = get_db()
            for indice in range(2, 7):
                db.execute(
                    "INSERT INTO anuncios "
                    "(usuario_id, titulo, descricao, preco, categoria, condicao, "
                    "ativo, estoque) VALUES (?,?,?,?,?,?,1,1)",
                    (
                        self.vendedor_id,
                        f"Produto integral {indice}",
                        "Produto para validar a reversÃ£o da vitrine.",
                        f"{indice}5,00",
                        "Outros",
                        "Usado",
                    ),
                )
            db.commit()

        with patch.object(app_module, "HOME_CIDADE_VIVA_ENABLED", True):
            html = self.client.get("/?todos=1").data.decode("utf-8")

        self.assertNotIn("home-city-alive", html)
        self.assertNotIn("Cidade Viva", html)
        self.assertEqual(html.count('class="card home-product-card"'), 6)
        self.assertIn('id="confianca"', html)
        self.assertIn('id="hoje-em-colatina"', html)

    def test_cidade_viva_css_mantem_flag_e_breakpoints_isolados(self):
        caminho_css = os.path.join(app.static_folder, "styles.css")
        with open(caminho_css, encoding="utf-8") as arquivo:
            css = arquivo.read()

        self.assertIn(".home-city-alive main", css)
        self.assertIn(".home-city-alive .home-product-showcase>.grid", css)
        self.assertIn("grid-template-columns:repeat(4,minmax(0,1fr))", css)
        self.assertIn("@media(max-width:960px)", css)
        self.assertIn("@media(max-width:640px)", css)
        self.assertIn("scroll-snap-type:x mandatory", css)

    def test_patch_ux_006a_posiciona_cidade_viva_apos_encontre_quem_resolve(self):
        with patch.object(app_module, "HOME_CIDADE_VIVA_ENABLED", True):
            html = self.client.get("/").data.decode("utf-8")

        self.assertIn("home-compact-ux006a", html)
        self.assertIn('<span aria-hidden="true">🌇</span> Cidade Viva', html)
        self.assertLess(
            html.index('class="home-solver-strip"'),
            html.index("data-home-city-movement"),
        )
        self.assertLess(
            html.index("data-home-city-movement"),
            html.index("data-ux005c-categories"),
        )

    def test_patch_ux_006a_oferece_ver_todos_em_todos_os_resumos(self):
        with patch.object(app_module, "HOME_CIDADE_VIVA_ENABLED", True):
            html = self.client.get("/").data.decode("utf-8")

        destinos = (
            "#hoje-em-colatina",
            "#categories-title",
            "#ofertas",
            "#ofertas-parceiros",
            "#home-stores-title",
            "#empresas-parceiras",
        )
        for destino in destinos:
            self.assertIn(f"?todos=1{destino}", html)
        self.assertGreaterEqual(html.count(">Ver todos</a>"), 6)

    def test_patch_ux_006a_flag_desligada_preserva_listas_integrais(self):
        html = self.client.get("/").data.decode("utf-8")

        self.assertNotIn("home-compact-ux006a", html)
        self.assertEqual(html.count('class="home-category-card'), 10)
        self.assertEqual(html.count("data-partner-card"), 6)
        self.assertEqual(html.count("data-affiliate-offer"), 6)

    def test_patch_ux_006a_css_compacta_somente_com_feature_flag(self):
        caminho_css = os.path.join(app.static_folder, "styles.css")
        with open(caminho_css, encoding="utf-8") as arquivo:
            css = arquivo.read()

        self.assertIn(".home-compact-ux006a .home-city-movement{order:25}", css)
        self.assertIn(
            ".home-compact-ux006a .home-category-card:nth-child(n+6){display:none}",
            css,
        )
        self.assertIn(
            ".home-compact-ux006a .partner-offer-card:nth-child(n+4){display:none}",
            css,
        )
        self.assertIn(
            ".home-compact-ux006a .home-local-partner-card:nth-child(n+4){display:none}",
            css,
        )

    def test_home_exibe_qr_code_oficial_para_acessar_o_site(self):
        html = self.client.get("/").data.decode("utf-8")

        self.assertIn('id="acessar-pelo-celular"', html)
        self.assertIn("QR Code para acessar o site Mercado Colatina", html)
        self.assertIn("qr-mercado-colatina.svg", html)
        self.assertGreaterEqual(html.count('href="https://mercadocolatina.com.br/"'), 2)

        resposta_qr = self.client.get("/static/qr-mercado-colatina.svg")
        self.assertEqual(resposta_qr.status_code, 200)
        self.assertIn("image/svg+xml", resposta_qr.content_type)

    def test_comunicado_global_renderiza_compacto_expansivel_e_fechavel(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO comunicados "
                "(titulo, mensagem, tipo, criado_por, ativo) VALUES (?,?,?,?,1)",
                (
                    "🏅 Programa Fundadores",
                    "Você faz parte dos primeiros usuários. Comunicado completo.",
                    "informacao",
                    self.admin_id,
                ),
            )
            db.commit()

        pagina = self.client.get("/")
        html = pagina.data.decode("utf-8")
        self.assertIn('class="announcement-details"', html)
        self.assertIn("Ler comunicado", html)
        self.assertIn("Ocultar comunicado", html)
        self.assertIn("data-announcement-dismiss", html)
        self.assertIn("Fechar comunicado", html)

    def test_home_exibe_secao_propria_com_as_lojas_ativas(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "UPDATE usuarios SET loja_nome='Pedal Colatina', loja_bairro='Centro' "
                "WHERE id=?",
                (self.vendedor_id,),
            )
            db.execute(
                "UPDATE anuncios SET visualizacoes=12 WHERE id=?",
                (self.anuncio_id,),
            )
            db.execute(
                "INSERT INTO pedidos "
                "(anuncio_id, comprador_id, vendedor_id, valor, status, entrega) "
                "VALUES (?,?,?,?,?,?)",
                (
                    self.anuncio_id,
                    self.comprador_id,
                    self.vendedor_id,
                    "1.200,00",
                    "concluido",
                    "retirada",
                ),
            )
            db.commit()

        self.autenticar_sessao(self.admin_id, admin=True)
        pagina = self.client.get("/")
        html = pagina.data.decode("utf-8")

        self.assertEqual(pagina.status_code, 200)
        self.assertIn('id="home-stores-title">Lojas em destaque', html)
        self.assertIn("Pedal Colatina", html)
        self.assertIn("Centro · Colatina, ES", html)
        self.assertIn("Anúncios</dt><dd>1", html)
        self.assertIn("Vendas</dt><dd>1", html)
        self.assertIn("Visualizações</dt><dd>12", html)
        self.assertIn(
            f'href="/loja/{self.vendedor_id}-pedal-colatina">Abrir loja</a>',
            html,
        )

    def test_loja_oficial_fica_fixa_na_primeira_posicao(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "UPDATE usuarios SET loja_nome='Loja Concorrente', "
                "loja_verificada=1 WHERE id=?",
                (self.vendedor_id,),
            )
            db.execute(
                "UPDATE usuarios SET loja_nome='Loja Oficial do Mercado Colatina' "
                "WHERE id=?",
                (self.comprador_id,),
            )
            db.execute(
                "INSERT INTO anuncios "
                "(usuario_id, titulo, descricao, preco, categoria, condicao, "
                "ativo, estoque, visualizacoes) VALUES (?,?,?,?,?,?,1,1,0)",
                (
                    self.comprador_id,
                    "Produto oficial",
                    "Produto da loja oficial.",
                    "50,00",
                    "Outros",
                    "Novo",
                ),
            )
            db.execute(
                "UPDATE anuncios SET visualizacoes=999 WHERE id=?",
                (self.anuncio_id,),
            )
            db.commit()

        with patch.object(app_module, "LOJA_OFICIAL_ID", self.comprador_id):
            html = self.client.get("/").data.decode("utf-8")

        inicio = html.index('<div class="home-stores-grid">')
        fim = html.index("</section>", inicio)
        vitrine = html[inicio:fim]
        self.assertLess(
            vitrine.index("Loja Oficial do Mercado Colatina"),
            vitrine.index("Loja Concorrente"),
        )
        self.assertIn("Loja oficial", vitrine)

    def test_ouvir_colatina_exibe_chamada_e_formulario_publico_acessivel(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        html_home = home.get_data(as_text=True)
        self.assertIn('class="community-suggestion-trigger"', html_home)
        self.assertIn('href="/sugerir"', html_home)
        self.assertIn("Sugira uma melhoria", html_home)

        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertIn("/sugerir", sitemap.get_data(as_text=True))

        privacidade = self.client.get("/privacidade")
        self.assertEqual(privacidade.status_code, 200)
        self.assertIn("Ouvir Colatina", privacidade.get_data(as_text=True))

        pagina = self.client.get("/sugerir")
        self.assertEqual(pagina.status_code, 200)
        html = pagina.get_data(as_text=True)
        self.assertIn("Está faltando alguma coisa em Colatina?", html)
        self.assertIn('for="sugestao-nome"', html)
        self.assertIn('for="sugestao-categoria"', html)
        self.assertIn('for="sugestao-mensagem"', html)
        self.assertIn('class="community-cancel-link" href="/"', html)
        self.assertIn("Cancelar e voltar", html)
        self.assertLess(html.index("Enviar sugestão"), html.index("Cancelar e voltar"))
        for categoria in (
            "Comércio",
            "Empresas",
            "Empregos",
            "Eventos",
            "Saúde",
            "Segurança",
            "Mobilidade",
            "Marketplace",
            "Cidade",
            "Outros",
        ):
            self.assertIn(categoria, html)

    def test_ouvir_colatina_aceita_nome_opcional_e_valida_conteudo(self):
        self.client.get("/sugerir")
        with self.client.session_transaction() as sessao:
            token = sessao["_csrf_token"]

        invalida = self.client.post(
            "/sugerir",
            data={
                "csrf_token": token,
                "nome": "",
                "categoria": "nao_existe",
                "mensagem": "Mensagem comunitária suficientemente detalhada.",
            },
        )
        self.assertEqual(invalida.status_code, 200)

        curta = self.client.post(
            "/sugerir",
            data={
                "csrf_token": token,
                "nome": "",
                "categoria": "mobilidade",
                "mensagem": "Curta",
            },
        )
        self.assertEqual(curta.status_code, 200)

        valida = self.client.post(
            "/sugerir",
            data={
                "csrf_token": token,
                "nome": "",
                "categoria": "mobilidade",
                "mensagem": "Precisamos organizar melhor as informações sobre mobilidade.",
            },
            follow_redirects=True,
        )
        self.assertEqual(valida.status_code, 200)
        self.assertIn("Sugestão enviada", valida.get_data(as_text=True))
        with app.app_context():
            sugestoes = (
                get_db()
                .execute(
                    "SELECT nome, categoria, mensagem, status FROM sugestoes_comunidade"
                )
                .fetchall()
            )
            self.assertEqual(len(sugestoes), 1)
            self.assertIsNone(sugestoes[0]["nome"])
            self.assertEqual(sugestoes[0]["categoria"], "mobilidade")
            self.assertEqual(sugestoes[0]["status"], "nova")

    def test_encontre_quem_resolve_exibe_fluxo_publico_em_quatro_passos(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        html_home = home.get_data(as_text=True)
        self.assertIn('class="find-solver-trigger"', html_home)
        self.assertIn('href="/encontre-quem-resolve"', html_home)

        pagina = self.client.get("/encontre-quem-resolve")
        self.assertEqual(pagina.status_code, 200)
        html = pagina.get_data(as_text=True)
        self.assertIn("O que você precisa resolver?", html)
        self.assertEqual(html.count("data-service-step="), 4)
        self.assertIn('maxlength="500"', html)
        self.assertNotIn('name="categoria"', html)
        self.assertIn("Sou empresa e quero ajudar", html)

        sitemap = self.client.get("/sitemap.xml").get_data(as_text=True)
        self.assertIn("/encontre-quem-resolve", sitemap)

    def test_encontre_quem_resolve_valida_publica_e_protege_whatsapp(self):
        self.client.get("/encontre-quem-resolve")
        with self.client.session_transaction() as sessao:
            token = sessao["_csrf_token"]

        sem_consentimento = self.client.post(
            "/encontre-quem-resolve",
            data={
                "csrf_token": token,
                "problema": "Meu chuveiro parou e preciso de um eletricista.",
                "bairro": "Centro",
                "urgencia": "hoje",
                "whatsapp": "(27) 99999-1234",
            },
        )
        self.assertEqual(sem_consentimento.status_code, 200)

        telefone_na_descricao = self.client.post(
            "/encontre-quem-resolve",
            data={
                "csrf_token": token,
                "problema": "Preciso de eletricista. Meu número é 27999991234.",
                "bairro": "Centro",
                "urgencia": "hoje",
                "whatsapp": "(27) 99999-1234",
                "consentimento": "sim",
            },
        )
        self.assertEqual(telefone_na_descricao.status_code, 200)
        self.assertIn(
            "Não coloque telefone na descrição",
            telefone_na_descricao.get_data(as_text=True),
        )

        valida = self.client.post(
            "/encontre-quem-resolve",
            data={
                "csrf_token": token,
                "problema": "Meu chuveiro parou e preciso de um eletricista.",
                "bairro": "Centro",
                "urgencia": "hoje",
                "whatsapp": "(27) 99999-1234",
                "consentimento": "sim",
            },
            follow_redirects=True,
        )
        self.assertEqual(valida.status_code, 200)
        self.assertIn("Pedido publicado", valida.get_data(as_text=True))

        with app.app_context():
            pedido = get_db().execute("SELECT * FROM pedidos_servico").fetchone()
            self.assertEqual(pedido["categoria"], "Casa e manutenção")
            self.assertEqual(pedido["whatsapp"], "5527999991234")
            self.assertEqual(pedido["status"], "aberto")

        oportunidades = self.client.get("/quem-resolve")
        html = oportunidades.get_data(as_text=True)
        self.assertIn("Meu chuveiro parou", html)
        self.assertNotIn("5527999991234", html)
        self.assertNotIn("99999-1234", html)

    def test_somente_loja_autenticada_pode_responder_pedido_local(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO pedidos_servico "
                "(problema, categoria, bairro, urgencia, whatsapp) "
                "VALUES (?,?,?,?,?)",
                (
                    "Preciso instalar uma tomada na cozinha.",
                    "Casa e manutenção",
                    "Maria das Graças",
                    "semana",
                    "5527999991234",
                ),
            )
            pedido_id = db.execute("SELECT id FROM pedidos_servico").fetchone()[0]
            db.commit()

        self.client.get("/quem-resolve")
        with self.client.session_transaction() as sessao:
            token = sessao["_csrf_token"]
        visitante = self.client.post(
            f"/quem-resolve/{pedido_id}/responder",
            data={"csrf_token": token},
        )
        self.assertEqual(visitante.status_code, 302)
        self.assertIn("/login", visitante.headers["Location"])

        self.autenticar_sessao(self.vendedor_id)
        sem_loja = self.client.post(
            f"/quem-resolve/{pedido_id}/responder",
            data={"csrf_token": "token-teste"},
        )
        self.assertEqual(sem_loja.status_code, 302)
        self.assertTrue(sem_loja.headers["Location"].endswith("/quem-resolve"))

        with app.app_context():
            db = get_db()
            db.execute(
                "UPDATE usuarios SET loja_nome='Eletricista Local' WHERE id=?",
                (self.vendedor_id,),
            )
            db.commit()
        resposta = self.client.post(
            f"/quem-resolve/{pedido_id}/responder",
            data={"csrf_token": "token-teste"},
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta.headers["Location"].startswith("https://wa.me/"))
        with app.app_context():
            total = (
                get_db()
                .execute(
                    "SELECT respostas FROM pedidos_servico WHERE id=?", (pedido_id,)
                )
                .fetchone()[0]
            )
            self.assertEqual(total, 1)

    def test_sugestoes_exigem_admin_e_painel_filtra_atualiza_e_mede(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO sugestoes_comunidade "
                "(nome, categoria, mensagem, status, criado_em) "
                "VALUES (?,?,?,?,datetime('now','-2 hours'))",
                ("Moradora", "saude", "Divulgar a farmácia de plantão.", "nova"),
            )
            db.execute(
                "INSERT INTO sugestoes_comunidade "
                "(nome, categoria, mensagem, status) VALUES (?,?,?,?)",
                (None, "eventos", "Organizar eventos do fim de semana.", "planejada"),
            )
            sugestao_id = db.execute(
                "SELECT id FROM sugestoes_comunidade WHERE categoria='saude'"
            ).fetchone()[0]
            db.commit()

        visitante = self.client.get("/admin/sugestoes")
        self.assertEqual(visitante.status_code, 302)
        self.autenticar_sessao(self.comprador_id)
        usuario = self.client.get("/admin/sugestoes")
        self.assertEqual(usuario.status_code, 302)

        self.autenticar_sessao(self.admin_id, admin=True)
        painel = self.client.get("/admin/sugestoes")
        self.assertEqual(painel.status_code, 200)
        html = painel.get_data(as_text=True)
        self.assertIn("Sugestões da comunidade", html)
        self.assertIn("Total de sugestões", html)
        self.assertIn("Categorias mais sugeridas", html)
        self.assertIn("Divulgar a farmácia de plantão.", html)
        self.assertIn("Organizar eventos do fim de semana.", html)

        filtrada = self.client.get("/admin/sugestoes?status=nova&categoria=saude")
        html_filtrado = filtrada.get_data(as_text=True)
        self.assertIn("Divulgar a farmácia de plantão.", html_filtrado)
        self.assertNotIn("Organizar eventos do fim de semana.", html_filtrado)

        resposta = self.client.post(
            f"/admin/sugestoes/{sugestao_id}/status",
            data={
                "csrf_token": "token-teste",
                "status": "implementada",
                "filtro_status": "todos",
                "filtro_categoria": "todas",
            },
            follow_redirects=True,
        )
        self.assertEqual(resposta.status_code, 200)
        html_atualizado = resposta.get_data(as_text=True)
        self.assertIn("Status da sugestão atualizado", html_atualizado)
        self.assertIn("Implementadas</span><strong>1", html_atualizado)
        self.assertIn("Tempo médio até análise</span><strong>2 h", html_atualizado)
        with app.app_context():
            sugestao = (
                get_db()
                .execute(
                    "SELECT status, analisada_em, implementada_em "
                    "FROM sugestoes_comunidade WHERE id=?",
                    (sugestao_id,),
                )
                .fetchone()
            )
            self.assertEqual(sugestao["status"], "implementada")
            self.assertIsNotNone(sugestao["analisada_em"])
            self.assertIsNotNone(sugestao["implementada_em"])

    def test_ouvir_colatina_preserva_analytics_e_componentes_anteriores(self):
        css = app.root_path + "/static/styles.css"
        with open(css, encoding="utf-8") as arquivo:
            estilos = arquivo.read()
        self.assertIn(".community-suggestion-trigger", estilos)
        self.assertIn("@media(max-width:900px)", estilos)
        self.assertIn("@media(max-width:640px)", estilos)
        self.assertIn("@media(max-width:359px)", estilos)
        self.assertIn(".notification-center", estilos)
        self.assertIn(".partner-offers", estilos)
        with app.app_context():
            db = get_db()
            self.assertEqual(
                db.execute("SELECT COUNT(*) FROM afiliado_eventos").fetchone()[0], 0
            )

    def test_inteligencia_comunidade_calcula_ranking_periodos_e_recorrencias(self):
        agora = datetime(2026, 7, 20, 12, 0, 0)
        registros = (
            (
                "saude",
                "Farmácia de plantão precisa divulgar médico e farmácia.",
                "nova",
                "2026-07-20 09:00:00",
                None,
                None,
            ),
            (
                "saude",
                "Farmácia e médico no bairro.",
                "em_analise",
                "2026-07-15 10:00:00",
                "2026-07-16 10:00:00",
                None,
            ),
            (
                "saude",
                "Atendimento médico na farmácia central.",
                "implementada",
                "2026-06-10 08:00:00",
                "2026-06-11 08:00:00",
                "2026-06-15 08:00:00",
            ),
            (
                "empregos",
                "Emprego e vagas para eletricista.",
                "planejada",
                "2026-07-10 12:00:00",
                None,
                None,
            ),
            (
                "empregos",
                "Emprego para eletricista e vagas.",
                "arquivada",
                "2026-05-30 12:00:00",
                "2026-06-01 12:00:00",
                None,
            ),
            (
                "eventos",
                "Eventos culturais no fim de semana.",
                "nova",
                "2026-04-01 12:00:00",
                None,
                None,
            ),
        )
        with app.app_context():
            db = get_db()
            for (
                categoria,
                mensagem,
                status,
                criada,
                analisada,
                implementada,
            ) in registros:
                db.execute(
                    "INSERT INTO sugestoes_comunidade "
                    "(categoria,mensagem,status,criado_em,analisada_em,implementada_em) "
                    "VALUES (?,?,?,?,?,?)",
                    (categoria, mensagem, status, criada, analisada, implementada),
                )
            db.commit()
            inteligencia = construir_inteligencia_comunidade(db, agora)
            dataset = construir_dataset_inteligencia(db, agora)

        self.assertEqual(inteligencia["total"], 6)
        self.assertEqual(inteligencia["pendentes"], 4)
        self.assertEqual(inteligencia["implementadas"], 1)
        self.assertEqual(inteligencia["arquivadas"], 1)
        self.assertEqual(inteligencia["tempo_medio_analise"], "1 d 8 h")
        self.assertEqual(
            [periodo["total"] for periodo in inteligencia["periodos"]],
            [1, 2, 3, 5],
        )
        self.assertEqual(
            [item["categoria"] for item in inteligencia["ranking_categorias"]],
            ["Saúde", "Empregos", "Eventos"],
        )
        self.assertEqual(
            inteligencia["categorias_crescimento"][0]["categoria"], "Saúde"
        )
        self.assertEqual(inteligencia["categorias_crescimento"][0]["variacao"], 1)
        palavras = {
            item["palavra"]: item["sugestoes"]
            for item in inteligencia["palavras_frequentes"]
        }
        self.assertEqual(palavras["Farmácia"], 3)
        self.assertEqual(palavras["Médico"], 3)
        self.assertEqual(palavras["Emprego"], 2)
        self.assertTrue(inteligencia["resposta_cidade"]["conclusiva"])
        self.assertEqual(inteligencia["resposta_cidade"]["titulo"], "Saúde")
        self.assertEqual(dataset["schema_version"], INTELLIGENCE_SCHEMA_VERSION)
        self.assertNotIn("nome", dataset["registros"][0])

    def test_inteligencia_comunidade_nao_inventa_tendencia_com_amostra_pequena(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO sugestoes_comunidade "
                "(categoria,mensagem,status) VALUES (?,?,?)",
                ("mobilidade", "Precisamos de mais horários de ônibus.", "nova"),
            )
            db.execute(
                "INSERT INTO sugestoes_comunidade "
                "(categoria,mensagem,status,criado_em) VALUES (?,?,?,datetime('now','-90 days'))",
                ("saude", "Farmácia com horário ampliado.", "arquivada"),
            )
            db.execute(
                "INSERT INTO sugestoes_comunidade "
                "(categoria,mensagem,status,criado_em) VALUES (?,?,?,datetime('now','-120 days'))",
                ("empregos", "Mais vagas de emprego local.", "implementada"),
            )
            db.commit()
            inteligencia = construir_inteligencia_comunidade(db)

        self.assertFalse(inteligencia["resposta_cidade"]["conclusiva"])
        self.assertEqual(
            inteligencia["resposta_cidade"]["titulo"],
            "Ainda não há dados suficientes",
        )
        self.assertIn("pelo menos 3", inteligencia["resposta_cidade"]["descricao"])

    def test_radar_da_cidade_e_exclusivo_do_admin_e_exibe_dados_agregados(self):
        mensagem = "Farmácia de plantão e atendimento médico no bairro central."
        with app.app_context():
            db = get_db()
            for indice in range(3):
                db.execute(
                    "INSERT INTO sugestoes_comunidade "
                    "(categoria,mensagem,status) VALUES (?,?,?)",
                    ("saude", f"{mensagem} Referência {indice}.", "nova"),
                )
            db.commit()

        self.assertEqual(
            self.client.get("/admin/inteligencia-comunidade").status_code, 302
        )
        self.autenticar_sessao(self.comprador_id)
        self.assertEqual(
            self.client.get("/admin/inteligencia-comunidade").status_code, 302
        )
        self.autenticar_sessao(self.admin_id, admin=True)
        resposta = self.client.get("/admin/inteligencia-comunidade")
        self.assertEqual(resposta.status_code, 200)
        html = resposta.get_data(as_text=True)
        self.assertIn("Radar da Cidade", html)
        self.assertIn("O que Colatina mais precisa neste momento?", html)
        self.assertIn("Sugestões por período", html)
        self.assertIn("Palavras mais frequentes", html)
        self.assertIn("Categorias em crescimento", html)
        self.assertIn("Sugestões recorrentes", html)
        self.assertIn("Problemas mais citados", html)
        self.assertIn("comunidade.v1", html)
        self.assertNotIn(mensagem, html)

    def test_radar_da_cidade_e_responsivo_e_preserva_modulos_anteriores(self):
        caminho_css = app.root_path + "/static/styles.css"
        with open(caminho_css, encoding="utf-8") as arquivo:
            estilos = arquivo.read()
        self.assertIn(".city-radar-shell", estilos)
        self.assertIn(".city-radar-grid{", estilos)
        self.assertIn("@media(max-width:900px)", estilos)
        self.assertIn("@media(max-width:640px)", estilos)
        self.assertIn("@media(max-width:359px)", estilos)
        self.assertIn(".notification-center", estilos)
        self.assertIn(".partner-offers", estilos)
        with app.app_context():
            db = get_db()
            self.assertEqual(
                db.execute("SELECT COUNT(*) FROM afiliado_eventos").fetchone()[0], 0
            )

    def test_tracao_classifica_origem_sem_persistir_dado_bruto(self):
        self.assertEqual(classify_access_source(), "direto")
        self.assertEqual(
            classify_access_source("https://www.instagram.com/mercado.colatina/"),
            "instagram",
        )
        self.assertEqual(
            classify_access_source("https://exemplo.com/pagina", "googleads"),
            "google",
        )
        self.assertEqual(
            classify_access_source("https://exemplo.com/pagina?segredo=1"),
            "outros",
        )
        with app.app_context():
            db = get_db()
            colunas = {
                linha[1]
                for linha in db.execute(
                    "PRAGMA table_info(traction_access_source_daily)"
                ).fetchall()
            }
        self.assertEqual(colunas, {"access_date", "source", "visits"})
        self.assertTrue({"ip", "referrer", "utm", "user_agent"}.isdisjoint(colunas))

    def test_tracao_agrega_origem_e_atividade_por_dia(self):
        with app.app_context():
            db = get_db()
            record_access_source(db, "google", "2026-07-20")
            record_access_source(db, "google", "2026-07-20")
            record_user_activity(db, self.comprador_id, "2026-07-20")
            record_user_activity(db, self.comprador_id, "2026-07-20")
            db.commit()
            origem = db.execute(
                "SELECT visits FROM traction_access_source_daily "
                "WHERE access_date=? AND source=?",
                ("2026-07-20", "google"),
            ).fetchone()[0]
            atividade = db.execute(
                "SELECT sessions FROM traction_user_activity_daily "
                "WHERE activity_date=? AND user_id=?",
                ("2026-07-20", self.comprador_id),
            ).fetchone()[0]
        self.assertEqual(origem, 2)
        self.assertEqual(atividade, 2)

    def test_dashboard_tracao_calcula_recorrencia_e_nao_inventa_receita(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "UPDATE usuarios SET loja_nome='Loja Vendedor' WHERE id=?",
                (self.vendedor_id,),
            )
            record_user_activity(db, self.comprador_id, "2026-07-10")
            record_user_activity(db, self.comprador_id, "2026-07-20")
            record_access_source(db, "whatsapp", "2026-07-20")
            db.commit()
            dados = build_traction_dashboard(
                db,
                app_module.OFERTAS_PARCEIROS_HOME,
                app_module.LOCAL_PARTNERS_HOME,
                datetime(2026, 7, 20, 15, tzinfo=timezone.utc),
            )
        self.assertEqual(dados["users"]["recorrentes"], 1)
        self.assertEqual(dados["users"]["retorno_rotulo"], "100.0%")
        self.assertEqual(dados["companies"]["cadastradas"], 1)
        self.assertEqual(dados["companies"]["ativas"], 1)
        self.assertEqual(dados["companies"]["convidadas_rotulo"], "Não mensurado")
        self.assertEqual(
            dados["affiliates"]["receita_rotulo"],
            "Não informada pelo parceiro",
        )
        self.assertEqual(dados["access_sources"][0]["source"], "whatsapp")

    def test_dashboard_tracao_e_relatorio_semanal_sao_exclusivos_do_admin(self):
        self.assertEqual(self.client.get("/admin?visao=dashboard").status_code, 302)
        self.assertEqual(
            self.client.get("/admin/operacao-tracao/relatorio-semanal.md").status_code,
            302,
        )
        self.autenticar_sessao(self.admin_id, admin=True)
        dashboard = self.client.get("/admin?visao=dashboard")
        self.assertEqual(dashboard.status_code, 200)
        html = dashboard.get_data(as_text=True)
        html = html.replace("&aacute;", chr(225)).replace("&oacute;", chr(243))
        for frente in (
            "usuarios",
            "empresas",
            "marketplace",
            "afiliados",
            "comunidade",
            "radar",
        ):
            self.assertIn(f'data-traction-front="{frente}"', html)
        self.assertIn("Baixar relatório semanal", html)
        relatorio = self.client.get("/admin/operacao-tracao/relatorio-semanal.md")
        self.assertEqual(relatorio.status_code, 200)
        self.assertIn(
            'filename="RELATORIO_EXECUTIVO_SEMANAL.md"',
            relatorio.headers["Content-Disposition"],
        )
        texto = relatorio.get_data(as_text=True)
        for secao in (
            "## Resumo da semana",
            "## Indicadores",
            "## Problemas encontrados",
            "## Oportunidades",
            "## Sugestões",
            "## Missão da próxima semana",
        ):
            self.assertIn(secao, texto)

    def test_tracao_e_responsiva_e_relatorio_usa_mesmos_dados(self):
        caminho_css = app.root_path + "/static/styles.css"
        with open(caminho_css, encoding="utf-8") as arquivo:
            estilos = arquivo.read()
        self.assertIn(".traction-grid", estilos)
        self.assertIn("@media(max-width:1100px)", estilos)
        self.assertIn("@media(max-width:700px)", estilos)
        self.assertIn("@media(max-width:359px)", estilos)
        with app.app_context():
            dados = build_traction_dashboard(
                get_db(),
                app_module.OFERTAS_PARCEIROS_HOME,
                app_module.LOCAL_PARTNERS_HOME,
                datetime(2026, 7, 20, 15, tzinfo=timezone.utc),
            )
        relatorio = render_weekly_report(dados)
        self.assertIn(str(dados["users"]["recorrentes"]), relatorio)
        self.assertIn(dados["marketplace"]["receita_plataforma_rotulo"], relatorio)
        self.assertIn(dados["affiliates"]["receita_rotulo"], relatorio)

    def test_operacao_100_calcula_funil_progressivo_e_marcos(self):
        with app.app_context():
            db = get_db()
            db.execute(
                "UPDATE usuarios SET criado_em='2026-07-15 12:00:00', "
                "loja_nome='Loja Vendedor' WHERE id=?",
                (self.vendedor_id,),
            )
            db.execute(
                "UPDATE usuarios SET criado_em='2026-07-15 12:00:00' WHERE id=?",
                (self.comprador_id,),
            )
            db.execute(
                "INSERT INTO pedidos (anuncio_id,comprador_id,vendedor_id,valor,status) "
                "VALUES (?,?,?,?,?)",
                (
                    self.anuncio_id,
                    self.comprador_id,
                    self.vendedor_id,
                    "1200.00",
                    "concluido",
                ),
            )
            record_access_source(db, "direto", "2026-07-18")
            record_access_source(db, "google", "2026-07-18")
            record_user_activity(db, self.vendedor_id, "2026-07-10")
            record_user_activity(db, self.vendedor_id, "2026-07-20")
            db.commit()
            data = build_operation_100_dashboard(
                db,
                app_module.OFERTAS_PARCEIROS_HOME,
                app_module.LOCAL_PARTNERS_HOME,
                datetime(2026, 7, 20, 15, tzinfo=timezone.utc),
            )
        values = {step["key"]: step["value"] for step in data["funnel"]["steps"]}
        self.assertEqual(values["visitor"], 2)
        self.assertEqual(values["registration"], 2)
        self.assertEqual(values["first_ad"], 1)
        self.assertEqual(values["first_order"], 1)
        self.assertEqual(values["first_sale"], 1)
        self.assertEqual(values["recurring"], 1)
        self.assertEqual(data["users"]["recurring"], 1)
        self.assertTrue(data["milestones"][0]["done"])
        self.assertFalse(data["milestones"][5]["automatic"])
        self.assertEqual(
            data["affiliates"]["revenue_label"],
            "N\u00e3o informada pelo parceiro",
        )

    def test_operacao_100_e_exclusiva_do_admin_e_exibe_todos_os_paineis(self):
        self.assertEqual(self.client.get("/admin/operacao-100").status_code, 302)
        self.autenticar_sessao(self.admin_id, admin=True)
        resposta = self.client.get("/admin/operacao-100")
        self.assertEqual(resposta.status_code, 200)
        html = resposta.get_data(as_text=True)
        for step in (
            "visitor",
            "registration",
            "first_ad",
            "first_order",
            "first_sale",
            "recurring",
        ):
            self.assertIn(f'data-funnel-step="{step}"', html)
        for section in (
            "Vis&atilde;o di&aacute;ria",
            "Funil de crescimento",
            "Empresas",
            "Comunidade",
            "Marcos oficiais",
            "O que impede o crescimento?",
        ):
            self.assertIn(section, html)

    def test_operacao_100_responsiva_e_sem_nova_tabela(self):
        with open(app.root_path + "/static/styles.css", encoding="utf-8") as arquivo:
            estilos = arquivo.read()
        self.assertIn(".operation-100-shell", estilos)
        self.assertIn("@media(max-width:1100px)", estilos)
        self.assertIn("@media(max-width:760px)", estilos)
        self.assertIn("@media(max-width:359px)", estilos)
        with app.app_context():
            tabelas = {
                row[0]
                for row in get_db()
                .execute("SELECT name FROM sqlite_master WHERE type='table'")
                .fetchall()
            }
        self.assertNotIn("operation_100", tabelas)

    def test_tracao_comercial_registra_empresa_embaixador_e_missao_unica(self):
        now = datetime(2026, 7, 20, 15, tzinfo=timezone.utc)
        with app.app_context():
            db = get_db()
            create_company(
                db,
                "Padaria Centro",
                "27999990000",
                "Centro",
                2,
                True,
                self.admin_id,
            )
            company_id = db.execute(
                "SELECT id FROM growth_commercial_companies"
            ).fetchone()[0]
            self.assertTrue(
                update_company_checklist(
                    db,
                    company_id,
                    {
                        "visits_count": "3",
                        "interested": "on",
                        "registered": "on",
                        "ad_published": "on",
                        "first_order": "on",
                        "partner": "on",
                        "referred_other": "on",
                    },
                )
            )
            create_ambassador(
                db,
                "Maria Bairro",
                "27999991111",
                "Centro",
                2,
                5,
                "Visitas e divulgacao local",
            )
            create_weekly_mission(
                db,
                "Conseguir cinco empresas",
                "empresas_cadastradas",
                5,
                self.admin_id,
                now,
            )
            create_weekly_mission(
                db,
                "Visitar o bairro Centro",
                "empresas_visitadas",
                10,
                self.admin_id,
                now,
            )
            data = build_commercial_dashboard(db, now)
            active_missions = db.execute(
                "SELECT COUNT(*) FROM growth_weekly_missions WHERE active=1"
            ).fetchone()[0]
        self.assertEqual(data["metrics"]["visited"], 1)
        self.assertEqual(data["metrics"]["registered"], 1)
        self.assertEqual(data["metrics"]["partners"], 1)
        self.assertEqual(data["metrics"]["visits"], 3)
        self.assertEqual(data["metrics"]["conversion_label"], "100.0%")
        self.assertEqual(len(data["ambassadors"]), 1)
        self.assertEqual(data["mission"]["title"], "Visitar o bairro Centro")
        self.assertEqual(active_missions, 1)

    def test_relatorio_comercial_usa_metricas_reais_e_identifica_previa(self):
        with app.app_context():
            data = build_commercial_dashboard(
                get_db(), datetime(2026, 7, 20, 15, tzinfo=timezone.utc)
            )
        report = render_commercial_weekly_report(data)
        self.assertIn("**Status:** Previa da semana", report)
        self.assertIn("## Empresas conquistadas", report)
        self.assertIn("## Indicadores da plataforma", report)
        self.assertIn("## Missao seguinte", report)

    def test_tracao_comercial_e_exclusiva_do_admin_e_protegida_por_csrf(self):
        self.assertEqual(self.client.get("/admin/tracao-comercial").status_code, 302)
        self.autenticar_sessao(self.admin_id, admin=True)
        page = self.client.get("/admin/tracao-comercial")
        self.assertEqual(page.status_code, 200)
        html = page.get_data(as_text=True)
        for marker in (
            'data-commercial-metric="visited"',
            "Miss&atilde;o da semana",
            "Empresas",
            "Embaixadores",
            "Relat&oacute;rio executivo de sexta-feira",
        ):
            self.assertIn(marker, html)
        rejected = self.client.post(
            "/admin/tracao-comercial/empresas",
            data={"name": "Sem token", "neighborhood": "Centro"},
        )
        self.assertEqual(rejected.status_code, 302)
        with app.app_context():
            self.assertEqual(
                get_db()
                .execute("SELECT COUNT(*) FROM growth_commercial_companies")
                .fetchone()[0],
                0,
            )
        created = self.client.post(
            "/admin/tracao-comercial/empresas",
            data={
                "csrf_token": "token-teste",
                "name": "Loja Nova",
                "contact": "27999992222",
                "neighborhood": "Sao Silvano",
                "visits_count": "1",
                "interested": "on",
            },
        )
        self.assertEqual(created.status_code, 302)
        report = self.client.get("/admin/tracao-comercial/relatorio-semanal.md")
        self.assertEqual(report.status_code, 200)
        self.assertIn(
            'filename="RELATORIO_EXECUTIVO_CONQUISTAR_COLATINA.md"',
            report.headers["Content-Disposition"],
        )

    def test_tracao_comercial_cria_apenas_tabelas_isoladas_e_e_responsiva(self):
        with app.app_context():
            db = get_db()
            tables = {
                row[0]
                for row in db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            company_columns = {
                row[1]
                for row in db.execute(
                    "PRAGMA table_info(growth_commercial_companies)"
                ).fetchall()
            }
        self.assertTrue(
            {
                "growth_commercial_companies",
                "growth_ambassadors",
                "growth_weekly_missions",
            }.issubset(tables)
        )
        self.assertTrue(
            {"contact", "neighborhood", "created_by"}.issubset(company_columns)
        )
        with open(app.root_path + "/static/styles.css", encoding="utf-8") as file:
            styles = file.read()
        self.assertIn(".commercial-growth-shell", styles)
        self.assertIn("@media(max-width:800px)", styles)
        self.assertIn("@media(max-width:500px)", styles)
        self.assertIn("@media(max-width:359px)", styles)

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
