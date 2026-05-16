import unittest
from unittest.mock import patch, MagicMock
import os
import json
from arch_gen.config import load_config, DEFAULT_LAYER_CONFIG

class TestConfig(unittest.TestCase):
    def test_load_config_success(self):
        mock_data = {
            "solution": "TestApp",
            "namespace": "TestCorp",
            "shared": {"layers": ["domain"]}
        }
        with patch("builtins.open", unittest.mock.mock_open(read_data=json.dumps(mock_data))):
            with patch("os.path.exists", return_value=True):
                config = load_config("fake.json")
                self.assertEqual(config["solution"], "TestApp")
                self.assertIn("_layer_config", config)
                self.assertEqual(config["_layer_config"]["domain"]["template"], "classlib")

if __name__ == "__main__":
    unittest.main()
