import os
import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from google_ads_service import get_google_ads_snapshot, reset_google_ads_cache


GOOGLE_ADS_ENV = {
    "GOOGLE_ADS_CUSTOMER_ID": "333-169-5325",
    "GOOGLE_ADS_DEVELOPER_TOKEN": "developer-token-test",
    "GOOGLE_ADS_CLIENT_ID": "client-id-test",
    "GOOGLE_ADS_CLIENT_SECRET": "client-secret-test",
    "GOOGLE_ADS_REFRESH_TOKEN": "refresh-token-test",
    "GOOGLE_ADS_API_VERSION": "v25",
}


def response(payload):
    result = Mock()
    result.raise_for_status.return_value = None
    result.json.return_value = payload
    return result


class GoogleAdsServiceTestCase(unittest.TestCase):
    def setUp(self):
        reset_google_ads_cache()

    def tearDown(self):
        reset_google_ads_cache()

    def test_sem_credenciais_usa_fallback_sem_fazer_requisicao(self):
        cleared = {name: "" for name in GOOGLE_ADS_ENV}
        with (
            patch.dict(os.environ, cleared, clear=False),
            patch("google_ads_service.requests.post") as post,
        ):
            snapshot = get_google_ads_snapshot()

        self.assertFalse(snapshot["connected"])
        self.assertEqual(snapshot["mode"], "Dados manuais de segurança")
        self.assertTrue(snapshot["missing"])
        post.assert_not_called()

    def test_sincroniza_metricas_oficiais_e_remove_hifens_do_cliente(self):
        api_payload = {
            "results": [
                {
                    "campaign": {
                        "id": "24087985650",
                        "name": "Pesquisa — Topa Tudo Colatinense — Campanha 001",
                        "status": "ENABLED",
                        "startDate": "2026-08-01",
                    },
                    "campaignBudget": {"amountMicros": "10000000"},
                    "metrics": {
                        "impressions": "125",
                        "clicks": "7",
                        "costMicros": "4250000",
                        "conversions": 1.0,
                    },
                }
            ]
        }
        with (
            patch.dict(os.environ, GOOGLE_ADS_ENV, clear=False),
            patch(
                "google_ads_service.requests.post",
                side_effect=[
                    response({"access_token": "access-token"}),
                    response(api_payload),
                ],
            ) as post,
        ):
            snapshot = get_google_ads_snapshot(
                now=datetime(2026, 8, 19, 12, 30, tzinfo=timezone.utc)
            )

        self.assertTrue(snapshot["connected"])
        self.assertEqual(snapshot["campaigns"][0]["metrics"]["impressions"], 125)
        self.assertEqual(snapshot["campaigns"][0]["metrics"]["cost"], 4.25)
        self.assertIn("customers/3331695325", post.call_args_list[1].args[0])
        self.assertNotIn(
            "client-secret-test", str(post.call_args_list[1].kwargs["headers"])
        )

    def test_cache_evitar_consultas_repetidas(self):
        with (
            patch.dict(os.environ, GOOGLE_ADS_ENV, clear=False),
            patch(
                "google_ads_service.requests.post",
                side_effect=[
                    response({"access_token": "token"}),
                    response({"results": []}),
                ],
            ) as post,
        ):
            first = get_google_ads_snapshot()
            second = get_google_ads_snapshot()

        self.assertIs(first, second)
        self.assertEqual(post.call_count, 2)


if __name__ == "__main__":
    unittest.main()
