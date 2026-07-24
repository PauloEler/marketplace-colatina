import unittest

from tools.seo_audit import normalize_internal_url, parse_html, sitemap_urls


class SEOAuditTestCase(unittest.TestCase):
    def test_parse_html_extrai_sinais_sem_executar_scripts(self):
        parser = parse_html(
            """<!doctype html><html><head>
            <title>Eletricista em Colatina | Mercado Colatina</title>
            <meta name="description" content="Encontre eletricista em Colatina.">
            <meta property="og:title" content="Eletricista em Colatina">
            <meta name="twitter:card" content="summary_large_image">
            <link rel="canonical" href="https://mercadocolatina.com.br/servicos/eletricista-colatina">
            <script type="application/ld+json">{}</script>
            </head><body><img src="ok.jpg" alt="Profissional eletricista"><a href="/servicos">Serviços</a></body></html>"""
        )
        self.assertEqual(parser.title, "Eletricista em Colatina | Mercado Colatina")
        self.assertEqual(parser.description, "Encontre eletricista em Colatina.")
        self.assertEqual(
            parser.canonical,
            "https://mercadocolatina.com.br/servicos/eletricista-colatina",
        )
        self.assertEqual(parser.json_ld_count, 1)
        self.assertEqual(parser.images_without_alt, [])
        self.assertIn("og:title", parser.open_graph)
        self.assertIn("twitter:card", parser.twitter_cards)

    def test_parse_html_identifica_imagem_sem_alt(self):
        parser = parse_html('<img src="sem-alt.jpg"><img src="decorativa.svg" alt="">')
        self.assertEqual(parser.image_count, 2)
        self.assertEqual(parser.images_without_alt, ["sem-alt.jpg"])

    def test_normalize_internal_url_remove_fragmento_e_ignora_query_ou_externo(self):
        base = "https://mercadocolatina.com.br"
        self.assertEqual(
            normalize_internal_url(
                base, f"{base}/", "/servicos/eletricista-colatina#contato"
            ),
            f"{base}/servicos/eletricista-colatina",
        )
        self.assertIsNone(normalize_internal_url(base, f"{base}/", "/?q=celular"))
        self.assertIsNone(
            normalize_internal_url(base, f"{base}/", "https://example.com")
        )

    def test_sitemap_urls_extrai_loc(self):
        xml = """<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://mercadocolatina.com.br/</loc></url></urlset>"""
        self.assertEqual(sitemap_urls(xml), ["https://mercadocolatina.com.br/"])


if __name__ == "__main__":
    unittest.main()
