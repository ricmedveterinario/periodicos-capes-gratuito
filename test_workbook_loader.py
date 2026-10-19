import ast
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import pandas as pd
from workbook_loader import open_workbook


class WorkbookLoadingTests(unittest.TestCase):
    def test_one_download_preserves_all_publisher_and_optional_tabs(self):
        source = ast.parse(Path(__file__).with_name("app.py").read_text(encoding="utf-8"))
        names = {"load_data", "parse_publishers_workbook"}
        functions = [node for node in source.body if isinstance(node, ast.FunctionDef) and node.name in names]
        for node in functions:
            node.decorator_list = []
        warnings = Mock()
        namespace = {"pd": pd, "open_workbook": open_workbook, "st": SimpleNamespace(warning=warnings)}
        exec(compile(ast.Module(body=functions, type_ignores=[]), "app.py", "exec"), namespace)
        publishers = {
            '🟡 Elsevier': 'Elsevier', '🟢 Springer Nature': 'Springer Nature',
            '🟢 Wiley OnlineOpen': 'Wiley OnlineOpen', '🟡 Wiley Gold': 'Wiley Gold',
            '🟢 ACM': 'ACM', '🔵 IEEE': 'IEEE', '💎 ACS': 'ACS',
            '🔴 RSP': 'Royal Society Publishing (RSP)',
        }
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for sheet, publisher in publishers.items():
                pd.DataFrame({"Titulo": [publisher], "Editora": [publisher]}).to_excel(writer, sheet_name=sheet, index=False)
            for sheet in ['📊 ÍNDICE', '✅ REQUISITOS', '⚠️ AVISOS']:
                pd.DataFrame({"Texto": [sheet]}).to_excel(writer, sheet_name=sheet, index=False)
        with patch("workbook_loader.urlopen") as download:
            download.return_value.__enter__.return_value.read.return_value = output.getvalue()
            result = namespace["load_data"]()
            download.assert_called_once()
            self.assertEqual(download.call_args.kwargs["timeout"], 30)
        self.assertEqual(len(result), 11)
        for publisher in publishers.values():
            self.assertEqual(result[publisher]["Titulo"].tolist(), [publisher])
            self.assertNotIn("Editora", result[publisher].columns)
        self.assertEqual(result["REQUISITOS"].columns.tolist(), ["Requisitos e Informações"])
        self.assertEqual(result["AVISOS"].columns.tolist(), ["⚠️ AVISOS IMPORTANTES"])
        warnings.assert_not_called()

    def test_download_failure_propagates(self):
        with patch("workbook_loader.urlopen", side_effect=TimeoutError("timeout")):
            with self.assertRaises(TimeoutError):
                open_workbook("https://example.com/data.xlsx")


if __name__ == "__main__":
    unittest.main()
