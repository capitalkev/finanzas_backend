import os
import base64
import pandas as pd

from src.infrastructure.create_pdfs.create import build_carta_pdf
from src.infrastructure.formato.formato import safe_filename, parse_amount_latam


class ExcelExtractionService:
    def __init__(self):
        self.SHEET_NAME = 0
        self.OUTPUT_DIR = "output_cartas_cesion"
        self.COL_DEUDOR = "Pagador/Garantizador"
        self.COL_RUC = "RUT Pagador/Garantizador"
        self.COL_MONTO = "Monto Factura"
        self.COL_NUMDOC = "Folio"
        self.COL_MONEDA = "Moneda"
        self.COL_VENC = "Fecha Venc. PuertoX"
        self.COL_TENEDOR = "Tenedor"
        self.COL_FECHA_INGRESO = "Fecha Ingreso"
        self.TENEDOR_VALIDO = "Toesca Deuda Privada Oportunidades USD FIP"

    def extract_and_convert_to_base64(
        self, file_stream, fecha_ingreso_desde_str: str
    ) -> list[dict]:
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        df = pd.read_excel(file_stream, sheet_name=self.SHEET_NAME, engine="openpyxl")

        df[self.COL_FECHA_INGRESO] = pd.to_datetime(
            df[self.COL_FECHA_INGRESO], format="%d-%m-%Y", errors="coerce"
        )
        fecha_desde = pd.to_datetime(
            fecha_ingreso_desde_str, format="%d-%m-%Y", errors="raise"
        )

        df = df[df[self.COL_TENEDOR] == self.TENEDOR_VALIDO]
        df = df[df[self.COL_FECHA_INGRESO] >= fecha_desde]

        df_work = pd.DataFrame(
            {
                "deudor": df[self.COL_DEUDOR],
                "ruc": df[self.COL_RUC],
                "numdoc": df[self.COL_NUMDOC],
                "vencimiento": df[self.COL_VENC],
                "monto_raw": df[self.COL_MONTO],
                "moneda": df[self.COL_MONEDA],
            }
        )

        df_work["deudor"] = df_work["deudor"].astype(str).str.strip()
        df_work = df_work[df_work["deudor"].notna() & (df_work["deudor"] != "")]
        df_work["monto_num"] = df_work["monto_raw"].apply(parse_amount_latam)

        # 2. Limpiar el RUC: Lo convertimos a string, quitamos el guion y los espacios
        df_work["ruc"] = (
            df_work["ruc"].astype(str).str.replace("-", "", regex=False).str.strip()
        )

        # Como los nulos al pasarlos a string se vuelven la palabra "nan", los convertimos nuevamente a None para un chequeo limpio
        df_work.loc[df_work["ruc"] == "nan", "ruc"] = None

        resultados: list[dict] = []

        for deudor, group in df_work.groupby("deudor", dropna=True):
            deudor_str = str(deudor)

            out_file = f"Carta_Cesion_{safe_filename(deudor_str)}.pdf"
            out_path = os.path.join(self.OUTPUT_DIR, out_file)

            build_carta_pdf(deudor_str, group, out_path)

            monto_total = float(group["monto_num"].sum())

            with open(out_path, "rb") as f:
                pdf_b64 = base64.b64encode(f.read()).decode("utf-8")

            os.remove(out_path)

            ruc_val = group["ruc"].iloc[0]

            resultados.append(
                {
                    "id": safe_filename(deudor_str),
                    # Por si Mypy se queja del ruc, también nos aseguramos de que sea string o "N/A"
                    "ruc": str(ruc_val) if pd.notna(ruc_val) else "N/A",
                    "nombre": deudor_str,
                    "correos": [],
                    "montoTotal": monto_total,
                    "pdfGenerado": out_file,
                    "pdfBase64": pdf_b64,
                }
            )

        return resultados
