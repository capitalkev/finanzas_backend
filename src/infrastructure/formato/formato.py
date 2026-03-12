import re
import pandas as pd


def safe_filename(name: str) -> str:
    name = str(name).strip()
    name = re.sub(r"[^\w\s.-]", "", name, flags=re.UNICODE)
    name = re.sub(r"\s+", "_", name)
    return name[:120] if name else "SIN_NOMBRE"


def format_date_es(value) -> str:
    if pd.isna(value):
        return ""
    ts = pd.to_datetime(value, errors="coerce", dayfirst=True)
    if pd.isna(ts):
        return str(value)
    return ts.strftime("%d/%m/%Y")


def parse_amount_latam(value):
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)

    s = str(value).strip()
    s = re.sub(r"[^0-9,.\-]", "", s)

    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s and "." not in s:
        s = s.replace(",", ".")

    try:
        return float(s)
    except:
        return None


def format_amount_es(value) -> str:
    if value is None or pd.isna(value):
        return ""
    x = float(value)
    s = f"{x:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def normalize_currency(cur) -> str:
    if pd.isna(cur):
        return ""
    c = str(cur).strip().upper()
    if c in ["PEN", "S/", "S/.", "SOLES", "SOL"]:
        return "S/"
    if c in ["USD", "US$", "$", "DOLARES", "DÓLARES"]:
        return "USD"
    return str(cur).strip()