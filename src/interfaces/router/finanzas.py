# src/interfaces/router/finanzas.py
import json
from fastapi import APIRouter, File, UploadFile, Form, Depends

from src.application.operacion_finanzas.operacion_finanzas import RobotOperacion

from src.infrastructure.excel_extraction.extraction_excel import ExcelExtraction

router = APIRouter(prefix="/finanzas", tags=["finanzas"])

@router.post("/extract")
async def extract_excel(
    excel: UploadFile = File(...),
    fecha_ingreso_desde: str = Form(...),
):
    excel_extraction = ExcelExtraction()
    resultados = excel_extraction.extract_data(excel.file, fecha_ingreso_desde)
    return {"data": resultados}
    

@router.post("/enviar-cartas")
async def enviar_cartas(
    pdfs: list[UploadFile] = File(...),
    datos_envio: str = Form(...),
    fecha_carpeta: str = Form(...),
    action: RobotOperacion = Depends()
):
    configuracion_envios = json.loads(datos_envio)
    
    return await action.execute(
        pdf_files=pdfs,
        configuracion_envios=configuracion_envios,
        nombre_carpeta=f"Cartas de cesión - {fecha_carpeta}"
    )