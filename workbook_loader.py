"""Download each remote workbook once and reuse it for all worksheets."""

from io import BytesIO
from urllib.request import urlopen

import pandas as pd


def download_workbook(url, timeout=30):
    """Bound network waits and keep the response in memory for Excel parsing."""
    with urlopen(url, timeout=timeout) as response:
        return BytesIO(response.read())


def open_workbook(url):
    return pd.ExcelFile(download_workbook(url), engine="openpyxl")
