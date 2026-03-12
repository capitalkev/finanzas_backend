from src.domain
from src.infrastructure.create_pdfs.create import build_carta_pdf
import os
import pandas as pd


class ExcelExtraction:
    def __init__(self):
        pass
    
    def extract_data(self, file_path):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME, engine="openpyxl")
    # Convertir Fecha Ingreso a datetime (formato DD-MM-YYYY)
    df[COL_FECHA_INGRESO] = pd.to_datetime(
    df[COL_FECHA_INGRESO],
    format="%d-%m-%Y",
    errors="coerce"
    )
    # Filtro 1: solo tenedor específico
    df = df[df[COL_TENEDOR] == TENEDOR_VALIDO]
    # Filtro 2: Fecha Ingreso desde la fecha ingresada por el usuario
    df = df[df[COL_FECHA_INGRESO] >= fecha_ingreso_desde]

    required = [COL_DEUDOR, COL_MONTO, COL_NUMDOC, COL_MONEDA, COL_VENC]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas en el Excel: {missing}")

    df_work = pd.DataFrame({
        "deudor": df[COL_DEUDOR],
        "numdoc": df[COL_NUMDOC],
        "vencimiento": df[COL_VENC],
        "monto_raw": df[COL_MONTO],
        "moneda": df[COL_MONEDA],
    })

    df_work["deudor"] = df_work["deudor"].astype(str).str.strip()
    df_work = df_work[df_work["deudor"].notna() & (df_work["deudor"] != "")]

    df_work["monto_num"] = df_work["monto_raw"].apply(parse_amount_latam)

    for deudor, group in df_work.groupby("deudor", dropna=True):
        out_file = f"Carta_Cesion_{safe_filename(deudor)}.pdf"
        out_path = os.path.join(OUTPUT_DIR, out_file)
        build_carta_pdf(deudor, group, out_path)
        print(f"OK -> {out_path}")