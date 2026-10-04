import os
import tempfile
import unittest

os.environ["CREATE_APP_ON_IMPORT"] = "0"  # tests build their own app with a temp model

from app.main import create_app  # noqa: E402
from app.train import train  # noqa: E402


class IrisApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.model_path = os.path.join(cls.tmp.name, "m.joblib")
        cls.accuracy = train(cls.model_path)
        cls.client = create_app(cls.model_path).test_client()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    # 1
    def test_health_endpoint_returns_ok(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json(), {"status": "ok"})

    # 2
    def test_predict_setosa(self):
        r = self.client.post("/predict", json={"features": [5.1, 3.5, 1.4, 0.2]})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["prediction"], "setosa")

    # 3
    def test_predict_virginica_and_probabilities_sum_to_one(self):
        r = self.client.post("/predict", json={"features": [6.7, 3.0, 5.2, 2.3]})
        body = r.get_json()
        self.assertEqual(body["prediction"], "virginica")
        self.assertAlmostEqual(sum(body["probabilities"].values()), 1.0, places=2)

    # 4
    def test_missing_features_returns_400(self):
        r = self.client.post("/predict", json={"wrong": 1})
        self.assertEqual(r.status_code, 400)

    # 5
    def test_wrong_number_of_features_returns_400(self):
        r = self.client.post("/predict", json={"features": [1, 2, 3]})
        self.assertEqual(r.status_code, 400)

    # 6
    def test_non_numeric_features_return_400(self):
        r = self.client.post("/predict", json={"features": ["a", "b", "c", "d"]})
        self.assertEqual(r.status_code, 400)

    # 7
    def test_model_accuracy_is_acceptable(self):
        self.assertGreaterEqual(self.accuracy, 0.85)

    # 8
    def test_info_endpoint_reports_hostname(self):
        r = self.client.get("/info")
        self.assertEqual(r.status_code, 200)
        self.assertIn("hostname", r.get_json())


if __name__ == "__main__":
    unittest.main()
