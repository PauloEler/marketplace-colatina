import unittest

from campaign_dashboard import CAMPAIGN_SNAPSHOTS, build_campaign_dashboard


class CampaignDashboardTestCase(unittest.TestCase):
    def test_snapshot_tem_duas_campanhas_unicas_e_somente_colatina(self):
        dashboard = build_campaign_dashboard()
        keys = [item["key"] for item in dashboard["campaigns"]]

        self.assertEqual(len(keys), 2)
        self.assertEqual(len(keys), len(set(keys)))
        self.assertTrue(
            all(item["location"] == "Colatina" for item in dashboard["campaigns"])
        )

    def test_zero_impressoes_nao_inventa_ctr(self):
        dashboard = build_campaign_dashboard()

        self.assertIsNone(dashboard["summary"]["ctr"])
        self.assertTrue(
            all(item["metrics"]["ctr"] is None for item in dashboard["campaigns"])
        )

    def test_snapshot_original_nao_e_mutado_pelo_builder(self):
        build_campaign_dashboard()

        self.assertTrue(
            all("ctr" not in item["metrics"] for item in CAMPAIGN_SNAPSHOTS)
        )

    def test_dados_automaticos_substituem_snapshot_por_id_e_nome(self):
        integration = {
            "connected": True,
            "mode": "Integração automática",
            "message": "Sincronizado.",
            "synced_at": "19/08/2026 · 09:30",
            "period": "Últimos 30 dias",
            "campaigns": (
                {
                    "campaign_id": "111",
                    "name": "Pesquisa — Mercado Colatina — Campanha 001",
                    "status": "ENABLED",
                    "started_at": "2026-08-01",
                    "daily_budget": 8.0,
                    "metrics": {
                        "impressions": 100,
                        "clicks": 5,
                        "cost": 7.5,
                        "conversions": 1.0,
                    },
                },
                {
                    "campaign_id": "24087985650",
                    "name": "Nome atualizado no Google",
                    "status": "PAUSED",
                    "started_at": "2026-08-01",
                    "daily_budget": 10.0,
                    "metrics": {
                        "impressions": 50,
                        "clicks": 2,
                        "cost": 3.0,
                        "conversions": 0.0,
                    },
                },
            ),
        }

        dashboard = build_campaign_dashboard(integration)

        self.assertEqual(dashboard["summary"]["impressions"], 150)
        self.assertEqual(dashboard["summary"]["clicks"], 7)
        self.assertEqual(dashboard["summary"]["cost"], 10.5)
        self.assertEqual(dashboard["campaigns"][0]["source"], "Google Ads API")
        self.assertEqual(dashboard["campaigns"][1]["status"], "Pausada")
        self.assertEqual(dashboard["data_mode"], "Integração automática")


if __name__ == "__main__":
    unittest.main()
