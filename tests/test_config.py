import unittest
from unittest.mock import patch, MagicMock
import os
import json
from arch_gen.config import load_config

class TestConfig(unittest.TestCase):
    def test_load_config_success(self):
        """Testa o carregamento bem-sucedido de um config válido."""
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

    @patch("os.path.exists", return_value=False)
    @patch("arch_gen.ui.sys.exit")
    def test_load_config_file_not_found(self, mock_exit, mock_exists):
        """Testa comportamento quando o arquivo não existe."""
        load_config("missing.json")
        mock_exit.assert_called_with(1)

    @patch("os.path.exists", return_value=True)
    @patch("arch_gen.ui.sys.exit")
    def test_load_config_invalid_json(self, mock_exit, mock_exists):
        """Testa comportamento com JSON malformado."""
        with patch("builtins.open", unittest.mock.mock_open(read_data="invalid json {")):
            load_config("bad.json")
            mock_exit.assert_called_with(1)

    @patch("os.path.exists", return_value=True)
    def test_load_config_layer_config_injection(self, mock_exists):
        """Garante que as configurações padrão de camadas são sempre injetadas."""
        mock_data = {"solution": "X"}
        with patch("builtins.open", unittest.mock.mock_open(read_data=json.dumps(mock_data))):
            config = load_config("fake.json")
            self.assertIn("_layer_config", config)
            self.assertIn("domain", config["_layer_config"])
            self.assertIn("application", config["_layer_config"])

if __name__ == "__main__":
    unittest.main()
