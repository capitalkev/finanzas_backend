# src/infrastructure/excel_extraction/extraction_excel.py
import os
import base64
import pandas as pd

from src.infrastructure.create_pdfs.create import build_carta_pdf
from src.infrastructure.formato.formato import safe_filename, parse_amount_latam

class ExcelExtraction:
    def __init__(self):
        self.SHEET_NAME = 0
        self.OUTPUT_DIR = "output_cartas_cesion"
        self.COL_DEUDOR = "Pagador/Garantizador"
        self.COL_MONTO = "Monto Factura"
        self.COL_NUMDOC = "Folio"
        self.COL_MONEDA = "Moneda"
        self.COL_VENC = "Fecha Venc. PuertoX"
        self.COL_TENEDOR = "Tenedor"
        self.COL_FECHA_INGRESO = "Fecha Ingreso"
        self.TENEDOR_VALIDO = "Toesca Deuda Privada Oportunidades USD FIP"

    def extract_data(self, file_stream, fecha_ingreso_desde_str: str) -> list[dict]:
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        df = pd.read_excel(file_stream, sheet_name=self.SHEET_NAME, engine="openpyxl")
        
        df[self.COL_FECHA_INGRESO] = pd.to_datetime(
            df[self.COL_FECHA_INGRESO], format="%d-%m-%Y", errors="coerce"
        )
        fecha_desde = pd.to_datetime(fecha_ingreso_desde_str, format="%d-%m-%Y", errors="raise")

        df = df[df[self.COL_TENEDOR] == self.TENEDOR_VALIDO]
        df = df[df[self.COL_FECHA_INGRESO] >= fecha_desde]

        df_work = pd.DataFrame({
            "deudor": df[self.COL_DEUDOR],
            "numdoc": df[self.COL_NUMDOC],
            "vencimiento": df[self.COL_VENC],
            "monto_raw": df[self.COL_MONTO],
            "moneda": df[self.COL_MONEDA],
        })

        df_work["deudor"] = df_work["deudor"].astype(str).str.strip()
        df_work = df_work[df_work["deudor"].notna() & (df_work["deudor"] != "")]
        df_work["monto_num"] = df_work["monto_raw"].apply(parse_amount_latam)

        resultados = []

        for deudor, group in df_work.groupby("deudor", dropna=True):
            out_file = f"Carta_Cesion_{safe_filename(deudor)}.pdf"
            out_path = os.path.join(self.OUTPUT_DIR, out_file)
            
            # Generar PDF físicamente
            build_carta_pdf(deudor, group, out_path)
            
            # Calcular monto total para el frontend
            monto_total = float(group["monto_num"].sum())
            
            # Leer como Base64 y eliminar archivo físico
            with open(out_path, "rb") as f:
                pdf_b64 = base64.b64encode(f.read()).decode('utf-8')
            os.remove(out_path)
            
            resultados.append({
                "id": safe_filename(deudor),
                "ruc": "N/A",
                "nombre": deudor,
                "montoTotal": monto_total,
                "pdfGenerado": out_file,
                "pdfBase64": pdf_b64
            })

        return resultados