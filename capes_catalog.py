"""Versioned input data and conservative checks for the CAPES catalogue."""
from datetime import date
import json
from pathlib import Path
import unicodedata

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
JOURNALS_FILE = "PUBLICA_ABERTO_CAPES_2026_2028_SITE_12_02_2026_v2.xlsx"
INSTITUTIONS_FILE = "instituicoes_elegiveis_FINAL_v2.xlsx"
DRIVE_FILES = {
    "periodicos": "1PysXi6_kp7TL4fXmw8jlZe5aFjRrWsSo",
    "instituicoes": "1zgE4_LshjeP75SqGzckP9bV36p_M_SS_",
}
REVISION = "2026-10-19"
PUBLISHERS = {
    "🟡 Elsevier": "Elsevier",
    "🟢 Springer Nature": "Springer Nature",
    "🟢 Wiley OnlineOpen": "Wiley OnlineOpen",
    "🟡 Wiley Gold": "Wiley Gold",
    "🟢 ACM": "ACM", "🔵 IEEE": "IEEE", "💎 ACS": "ACS",
    "🔴 RSP": "Royal Society Publishing (RSP)",
}


def normalize(value):
    if pd.isna(value):
        return ""
    return "".join(c for c in unicodedata.normalize("NFKD", str(value))
                   if not unicodedata.combining(c)).upper()


def prepare_search(frame):
    result = frame.copy()
    result["_busca"] = result.fillna("").astype(str).agg(lambda row: " ".join(map(str, row)), axis=1).map(normalize)
    if "ISSN" in result:
        result["_busca"] += " " + result["ISSN"].astype(str).str.replace("-", "", regex=False)
    return result


def search_catalog(frame, term):
    if not term:
        return frame
    return frame.loc[frame["_busca"].str.contains(normalize(term), regex=False, na=False)]


def acceptance_status(publisher, accepted):
    if publisher not in {"Springer Nature", "Nature Portfolio", "Elsevier"}:
        return "Conferir a vigência no acordo da editora"
    if accepted is None:
        return "Informe a data de aceite para conferir a vigência"
    start = date(2026, 9, 1) if publisher == "Nature Portfolio" else date(2026, 1, 1)
    return ("Dentro da vigência; demais requisitos pendentes"
            if start <= accepted <= date(2028, 12, 31) else "Fora da vigência do acordo")


def load_catalog(data_dir=None, service_account_info=None):
    """Read private Drive v2 files, or explicitly provided local files in tests."""
    if data_dir is not None:
        root = Path(data_dir)
        journals_source, institutions_source = root / JOURNALS_FILE, root / INSTITUTIONS_FILE
    else:
        from drive_workbooks import read_private_workbooks
        files = read_private_workbooks(service_account_info, DRIVE_FILES)
        journals_source, institutions_source = files['periodicos'], files['instituicoes']
    result = {}
    with pd.ExcelFile(journals_source, engine="openpyxl") as workbook:
        for sheet, publisher in PUBLISHERS.items():
            frame = pd.read_excel(workbook, sheet_name=sheet, dtype={"ISSN": str}).dropna(how="all").reset_index(drop=True)
            if not {"Título da Revista", "ISSN", "Modelo", "Cobertura APC"}.issubset(frame.columns):
                raise ValueError(f"Estrutura inválida: {sheet}")
            frame = frame.drop(columns=["Editora"], errors="ignore")
            frame["Situação da lista"] = ("Lista oficial Springer; conferir cobertura por título"
                                            if publisher == "Springer Nature" else
                                            "Lista anterior preservada; confirmar condições atuais na editora")
            if publisher == "Springer Nature":
                frame["Aceite inicial"] = "2026-01-01"
                frame["Aceite final"] = "2028-12-31"
            result[publisher] = prepare_search(frame)
        for key, sheet in [("INDICE", "📊 ÍNDICE"), ("REQUISITOS", "✅ REQUISITOS"), ("AVISOS", "⚠️ AVISOS")]:
            result[key] = pd.read_excel(workbook, sheet_name=sheet).dropna(how="all")
    institutions = pd.read_excel(institutions_source, engine="openpyxl", sheet_name=0).dropna(how="all")
    if list(institutions.columns) != ["Editora", "Sigla", "Nome da Instituição", "Busca (normalizado)"]:
        raise ValueError("Estrutura inválida da base de instituições")
    official = json.loads((DATA_DIR / "nature_2026.json").read_text(encoding="utf-8"))
    nature = pd.DataFrame(official["journals"])
    if len(nature) != 41 or nature["ISSN"].duplicated().any():
        raise ValueError("A lista Nature não corresponde aos 41 títulos conferidos")
    result["Nature Portfolio"] = prepare_search(nature)
    index = result['INDICE']
    nature_index = dict(zip(index.columns, ['Nature', 'Nature Portfolio', 'HÍBRIDOS', 'Conforme requisitos', 41,
                                           'Set/2026 - Dez/2028', 'Lista oficial Nature de 01/09/2026; instituições próprias']))
    result['INDICE'] = pd.concat([index, pd.DataFrame([nature_index])], ignore_index=True)
    result['REQUISITOS'] = result['REQUISITOS'].apply(lambda column: column.map(
        lambda value: value.replace('Nature de setembro/2026 está em revisão separada.',
                                   'Nature incluída em grupo separado: 41 títulos e lista institucional própria.').replace('TOTAL: 5.895 registros', 'TOTAL: 5.936 registros')
        if isinstance(value, str) else value))
    institution_rows = []
    acronyms = {}
    for name, acronym in institutions[["Nome da Instituição", "Sigla"]].dropna().itertuples(index=False, name=None):
        acronyms.setdefault(normalize(name), str(acronym))
    for portfolio, publisher in [("Springer", "Springer Nature"), ("Nature", "Nature Portfolio")]:
        for name in official["institutions"][portfolio]:
            # Use acronyms only when an exact normalized name already has one.
            acronym = acronyms.get(normalize(name), "")
            institution_rows.append({"Editora": publisher, "Sigla": acronym, "Nome da Instituição": name,
                                     "Busca (normalizado)": normalize(name + " " + acronym)})
    institutions = institutions.loc[institutions["Editora"] != "Springer Nature"]
    institutions = pd.concat([institutions, pd.DataFrame(institution_rows)], ignore_index=True)
    return result, institutions
