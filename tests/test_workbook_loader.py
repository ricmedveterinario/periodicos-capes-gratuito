from io import BytesIO
import unittest
from unittest.mock import patch

import pandas as pd
from workbook_loader import open_workbook


class WorkbookLoadingTests(unittest.TestCase):
    def test_one_download_preserves_all_publisher_and_optional_tabs(self):
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
            with open_workbook('https://example.com/data.xlsx') as workbook:
                result = {sheet: pd.read_excel(workbook, sheet_name=sheet) for sheet in workbook.sheet_names}
            download.assert_called_once()
            self.assertEqual(download.call_args.kwargs["timeout"], 30)
        self.assertEqual(len(result), 11)
        for sheet, publisher in publishers.items():
            self.assertEqual(result[sheet]["Titulo"].tolist(), [publisher])

    def test_download_failure_propagates(self):
        with patch("workbook_loader.urlopen", side_effect=TimeoutError("timeout")):
            with self.assertRaises(TimeoutError):
                open_workbook("https://example.com/data.xlsx")


if __name__ == "__main__":
    unittest.main()
