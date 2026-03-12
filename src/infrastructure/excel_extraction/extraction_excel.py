import os
import zipfile
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

    def extract_data(self, file_stream, fecha_ingreso_desde_str: str) -> str:
        """
        Procesa el excel, genera los PDFs y retorna la ruta del archivo ZIP generado.
        """
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        df = pd.read_excel(file_stream, sheet_name=self.SHEET_NAME, engine="openpyxl")
        
        df[self.COL_FECHA_INGRESO] = pd.to_datetime(
            df[self.COL_FECHA_INGRESO], format="%d-%m-%Y", errors="coerce"
        )
        fecha_desde = pd.to_datetime(fecha_ingreso_desde_str, format="%d-%m-%Y", errors="raise")

        df = df[df[self.COL_TENEDOR] == self.TENEDOR_VALIDO]
        df = df[df[self.COL_FECHA_INGRESO] >= fecha_desde]

        required = [self.COL_DEUDOR, self.COL_MONTO, self.COL_NUMDOC, self.COL_MONEDA, self.COL_VENC]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Faltan columnas en el Excel: {missing}")

        # Preparar datos de trabajo
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

        pdf_paths = []

        # Generar PDFs iterando por deudor
        for deudor, group in df_work.groupby("deudor", dropna=True):
            out_file = f"Carta_Cesion_{safe_filename(deudor)}.pdf"
            out_path = os.path.join(self.OUTPUT_DIR, out_file)
            build_carta_pdf(deudor, group, out_path)
            pdf_paths.append(out_path)
            print(f"OK -> {out_path}")

        # Comprimir todos los PDFs en un ZIP
        zip_filename = "cartas_cesion.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for pdf_path in pdf_paths:
                # Agregamos al zip solo el nombre del archivo, no toda la ruta
                zipf.write(pdf_path, os.path.basename(pdf_path))

        return zip_filename