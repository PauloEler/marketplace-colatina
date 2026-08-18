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


if __name__ == "__main__":
    unittest.main()
