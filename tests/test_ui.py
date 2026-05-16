import unittest
from unittest.mock import patch, MagicMock
import sys
from arch_gen.ui import ok, skip, warn, err, info

class TestUI(unittest.TestCase):
    @patch("builtins.print")
    def test_ui_methods_print(self, mock_print):
        ok("test ok")
        skip("test skip")
        warn("test warn")
        info("test info")
        self.assertTrue(mock_print.called)
        self.assertEqual(mock_print.call_count, 4)

    @patch("sys.exit")
    @patch("builtins.print")
    def test_ui_err_exits(self, mock_print, mock_exit):
        err("fatal error")
        mock_exit.assert_called_with(1)

if __name__ == "__main__":
    unittest.main()
